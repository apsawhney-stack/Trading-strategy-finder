"""
LLM-based strategy extraction using Google Gemini.
Extracts structured strategy data with confidence scores and source quotes.
"""

import json
import asyncio
from typing import Optional

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.models import (
    ExtractedStrategy,
    ExtractedField,
    ExtractedNumericField,
    SetupRules,
    ManagementRules,
    RiskProfile,
    PerformanceClaims,
    FailureModeAnalysis,
)

settings = get_settings()

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


# ============================================================================
# Extraction Prompt
# ============================================================================

EXTRACTION_PROMPT = """
You are an expert options trading analyst. Extract structured strategy data from the following transcript/content.

CRITICAL RULES:
1. For each field, provide:
   - value: The extracted value (string or number)
   - confidence: 0.0-1.0 based on how explicit the information is
   - source_quote: Exact quote from text (max 150 chars)
   - interpretation: "explicit" (directly stated), "implicit" (clearly implied), "inferred" (educated guess), "missing" (not found)

2. Distinguish interpretation types:
   - EXPLICIT: "I trade 30 DTE" → confidence: 1.0, interpretation: "explicit"
   - IMPLICIT: "Weekly options" → DTE: 7, confidence: 0.9, interpretation: "implicit"
   - INFERRED: "Short-term trades" → DTE: [5, 14], confidence: 0.5, interpretation: "inferred"
   - MISSING: Not mentioned at all → confidence: 0, interpretation: "missing"

3. IMPORTANT: Look for FAILURE MODES. If author only discusses wins, set bias_detected: true.

4. Extract key insights, warnings, and memorable quotes.

Return ONLY valid JSON matching this schema:

{
  "strategy_name": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "explicit|implicit|inferred|missing"},
  "variation": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
  "trader_name": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
  "experience_level": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
  
  "setup_rules": {
    "underlying": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "option_type": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "strike_selection": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "dte": {"value": 30, "value_range": [25, 45], "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "width": {"value": 10, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "delta": {"value": 0.16, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "entry_criteria": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "entry_timing": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "buying_power_effect": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."}
  },
  
  "management_rules": {
    "profit_target": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "stop_loss": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "time_exit": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "adjustment_rules": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "rolling_rules": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "defensive_maneuvers": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."}
  },
  
  "risk_profile": {
    "max_loss_per_trade": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "win_rate": {"value": 0.75, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "risk_reward_ratio": {"value": "string", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "max_drawdown": {"value": 15.0, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."}
  },
  
  "performance_claims": {
    "starting_capital": {"value": 3200, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "ending_capital": {"value": 12000, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "total_return_percent": {"value": 275.0, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "time_period": {"value": "9 months", "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "profits_withdrawn": {"value": 0, "confidence": 0.0-1.0, "source_quote": "string", "interpretation": "..."},
    "verified": false
  },
  
  "failure_analysis": {
    "failure_modes_mentioned": ["list of failure scenarios mentioned"],
    "discusses_losses": true/false,
    "max_drawdown_mentioned": 15.0 or null,
    "recovery_strategy": "string or null",
    "bias_detected": true/false
  },
  
  "key_insights": ["list of key takeaways"],
  "warnings": ["list of warnings or caveats mentioned"],
  "quotes": ["memorable direct quotes from the content"]
}

CONTENT TO ANALYZE:
---
{content}
---

Return ONLY the JSON, no markdown formatting, no code blocks.
"""


# ============================================================================
# Chunking for Long Transcripts
# ============================================================================

def chunk_text(text: str, chunk_size: int = 5000, overlap: int = 500) -> list[str]:
    """Split long text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks


# ============================================================================
# LLM Extraction
# ============================================================================

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_gemini(prompt: str) -> str:
    """Call Gemini API with retry logic."""
    model = genai.GenerativeModel(settings.gemini_model)
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: model.generate_content(prompt)
    )
    
    return response.text


def _parse_field(data: dict, key: str) -> ExtractedField:
    """Parse a field from JSON into ExtractedField."""
    if not data or key not in data:
        return ExtractedField()
    
    field_data = data[key]
    if isinstance(field_data, dict):
        return ExtractedField(
            value=str(field_data.get("value", "")) if field_data.get("value") else None,
            confidence=float(field_data.get("confidence", 0)),
            source_quote=field_data.get("source_quote"),
            interpretation=field_data.get("interpretation", "missing"),
        )
    return ExtractedField(value=str(field_data) if field_data else None, confidence=0.5)


def _parse_numeric_field(data: dict, key: str) -> ExtractedNumericField:
    """Parse a numeric field from JSON into ExtractedNumericField."""
    if not data or key not in data:
        return ExtractedNumericField()
    
    field_data = data[key]
    if isinstance(field_data, dict):
        value = field_data.get("value")
        value_range = field_data.get("value_range")
        return ExtractedNumericField(
            value=float(value) if value is not None else None,
            value_range=tuple(value_range) if value_range else None,
            confidence=float(field_data.get("confidence", 0)),
            source_quote=field_data.get("source_quote"),
            interpretation=field_data.get("interpretation", "missing"),
        )
    return ExtractedNumericField(value=float(field_data) if field_data else None, confidence=0.5)


def _parse_extraction(json_str: str) -> ExtractedStrategy:
    """Parse JSON string into ExtractedStrategy."""
    try:
        # Clean up JSON string (remove markdown code blocks if present)
        clean_json = json_str.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1]
            if clean_json.startswith("json"):
                clean_json = clean_json[4:]
        clean_json = clean_json.strip()
        
        data = json.loads(clean_json)
        
        return ExtractedStrategy(
            strategy_name=_parse_field(data, "strategy_name"),
            variation=_parse_field(data, "variation"),
            trader_name=_parse_field(data, "trader_name"),
            experience_level=_parse_field(data, "experience_level"),
            
            setup_rules=SetupRules(
                underlying=_parse_field(data.get("setup_rules", {}), "underlying"),
                option_type=_parse_field(data.get("setup_rules", {}), "option_type"),
                strike_selection=_parse_field(data.get("setup_rules", {}), "strike_selection"),
                dte=_parse_numeric_field(data.get("setup_rules", {}), "dte"),
                width=_parse_numeric_field(data.get("setup_rules", {}), "width"),
                delta=_parse_numeric_field(data.get("setup_rules", {}), "delta"),
                entry_criteria=_parse_field(data.get("setup_rules", {}), "entry_criteria"),
                entry_timing=_parse_field(data.get("setup_rules", {}), "entry_timing"),
                buying_power_effect=_parse_field(data.get("setup_rules", {}), "buying_power_effect"),
            ),
            
            management_rules=ManagementRules(
                profit_target=_parse_field(data.get("management_rules", {}), "profit_target"),
                stop_loss=_parse_field(data.get("management_rules", {}), "stop_loss"),
                time_exit=_parse_field(data.get("management_rules", {}), "time_exit"),
                adjustment_rules=_parse_field(data.get("management_rules", {}), "adjustment_rules"),
                rolling_rules=_parse_field(data.get("management_rules", {}), "rolling_rules"),
                defensive_maneuvers=_parse_field(data.get("management_rules", {}), "defensive_maneuvers"),
            ),
            
            risk_profile=RiskProfile(
                max_loss_per_trade=_parse_field(data.get("risk_profile", {}), "max_loss_per_trade"),
                win_rate=_parse_numeric_field(data.get("risk_profile", {}), "win_rate"),
                risk_reward_ratio=_parse_field(data.get("risk_profile", {}), "risk_reward_ratio"),
                max_drawdown=_parse_numeric_field(data.get("risk_profile", {}), "max_drawdown"),
            ),
            
            performance_claims=PerformanceClaims(
                starting_capital=_parse_numeric_field(data.get("performance_claims", {}), "starting_capital"),
                ending_capital=_parse_numeric_field(data.get("performance_claims", {}), "ending_capital"),
                total_return_percent=_parse_numeric_field(data.get("performance_claims", {}), "total_return_percent"),
                time_period=_parse_field(data.get("performance_claims", {}), "time_period"),
                profits_withdrawn=_parse_numeric_field(data.get("performance_claims", {}), "profits_withdrawn"),
                verified=data.get("performance_claims", {}).get("verified", False),
            ),
            
            failure_analysis=FailureModeAnalysis(
                failure_modes_mentioned=data.get("failure_analysis", {}).get("failure_modes_mentioned", []),
                discusses_losses=data.get("failure_analysis", {}).get("discusses_losses", False),
                max_drawdown_mentioned=data.get("failure_analysis", {}).get("max_drawdown_mentioned"),
                recovery_strategy=data.get("failure_analysis", {}).get("recovery_strategy"),
                bias_detected=data.get("failure_analysis", {}).get("bias_detected", True),
            ),
            
            key_insights=data.get("key_insights", []),
            warnings=data.get("warnings", []),
            quotes=data.get("quotes", []),
        )
        
    except json.JSONDecodeError as e:
        # Return empty extraction on parse failure
        return ExtractedStrategy()


async def extract_strategy_from_text(content: str) -> ExtractedStrategy:
    """
    Extract strategy data from text content using Gemini.
    Handles long content via chunking and map-reduce.
    """
    
    if not settings.gemini_api_key:
        # Return empty extraction if no API key
        return ExtractedStrategy()
    
    # Check content length
    if len(content) > settings.max_transcript_tokens * 4:  # Rough char-to-token estimate
        # Use map-reduce for long content
        chunks = chunk_text(content, settings.chunk_size, settings.chunk_overlap)
        
        # Extract from each chunk
        chunk_extractions = []
        for chunk in chunks:
            prompt = EXTRACTION_PROMPT.format(content=chunk)
            response = await _call_gemini(prompt)
            extraction = _parse_extraction(response)
            chunk_extractions.append(extraction)
        
        # Merge extractions (take highest confidence for each field)
        return _merge_extractions(chunk_extractions)
    else:
        # Single extraction
        prompt = EXTRACTION_PROMPT.format(content=content)
        response = await _call_gemini(prompt)
        return _parse_extraction(response)


def _merge_extractions(extractions: list[ExtractedStrategy]) -> ExtractedStrategy:
    """Merge multiple extractions, keeping highest confidence for each field."""
    if not extractions:
        return ExtractedStrategy()
    
    if len(extractions) == 1:
        return extractions[0]
    
    # For simplicity, take the extraction with highest average confidence
    best = extractions[0]
    best_score = 0
    
    for extraction in extractions:
        # Calculate average confidence across key fields
        confidences = [
            extraction.strategy_name.confidence,
            extraction.setup_rules.underlying.confidence,
            extraction.setup_rules.dte.confidence,
            extraction.management_rules.profit_target.confidence,
        ]
        avg_score = sum(confidences) / len(confidences)
        
        if avg_score > best_score:
            best = extraction
            best_score = avg_score
    
    # Merge insights, warnings, quotes from all extractions
    all_insights = []
    all_warnings = []
    all_quotes = []
    
    for extraction in extractions:
        all_insights.extend(extraction.key_insights)
        all_warnings.extend(extraction.warnings)
        all_quotes.extend(extraction.quotes)
    
    best.key_insights = list(set(all_insights))[:10]  # Dedupe and limit
    best.warnings = list(set(all_warnings))[:10]
    best.quotes = list(set(all_quotes))[:10]
    
    return best
