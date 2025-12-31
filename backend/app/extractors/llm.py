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

EXTRACTION_PROMPT_TEMPLATE = '''
You are an expert options trading analyst. Extract ALL strategy details from this content.

For each field provide: value, confidence (0-1), source_quote (exact text), interpretation (explicit/implicit/inferred/missing)

EXTRACT THESE FIELDS:

1. strategy_name: Name of the strategy (e.g., "Iron Condor", "0 DTE Put Credit Spread")
2. trader_name: Name of the person teaching/trading
3. setup_rules:
   - underlying: The ticker symbol (SPX, SPY, QQQ, etc.)
   - dte: Days to expiration (e.g., 0, 7, 30, 45)
   - delta: Delta target for strikes (e.g., 0.16, 0.30, "16 delta")
   - strike_selection: How strikes are chosen (e.g., "ATM", "5 points wide")
   - entry_criteria: When to enter (e.g., "IV rank above 30", "after market open")
   - option_type: Type of options (puts, calls, spreads)
   - width: Spread width in points (e.g., 5, 10, 25)

4. management_rules:
   - profit_target: When to take profit (e.g., "50%", "$100", "21 DTE")
   - stop_loss: When to exit for loss (e.g., "200%", "2x credit")
   - adjustment_rules: How to adjust losing positions
   - time_exit: When to exit based on time

5. risk_profile:
   - win_rate: Expected win percentage
   - max_drawdown: Worst expected loss

6. key_insights: List of key takeaways from the content
7. warnings: Any warnings or risks mentioned

IMPORTANT: Look carefully for numbers! Extract DTE (0, 7, 30, 45), delta (0.16, 0.30), profit targets (50%, 75%), stop losses.

Return ONLY valid JSON, no markdown, no explanation. Example:
<<<JSON_EXAMPLE>>>

CONTENT TO ANALYZE:
---
<<<CONTENT>>>
---
'''

JSON_EXAMPLE = '''{"strategy_name":{"value":"0 DTE Iron Fly","confidence":1.0,"source_quote":"zero DTE iron fly","interpretation":"explicit"},"setup_rules":{"underlying":{"value":"SPX","confidence":1.0},"dte":{"value":0,"confidence":1.0},"delta":{"value":0.16,"confidence":0.8},"profit_target":{"value":"50%","confidence":0.9}},"key_insights":["Average hold time 18 minutes","Focus on premium collection"],"warnings":["High risk strategy"]}'''


def build_extraction_prompt(content: str) -> str:
    """Build extraction prompt with content substituted."""
    prompt = EXTRACTION_PROMPT_TEMPLATE.replace('<<<CONTENT>>>', content)
    prompt = prompt.replace('<<<JSON_EXAMPLE>>>', JSON_EXAMPLE)
    return prompt


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
        quote = field_data.get("source_quote")
        if quote and len(quote) > 450:
            quote = quote[:447] + "..."
        return ExtractedField(
            value=str(field_data.get("value", "")) if field_data.get("value") else None,
            confidence=float(field_data.get("confidence", 0)) if field_data.get("confidence") else 0.0,
            source_quote=quote,
            interpretation=field_data.get("interpretation", "missing"),
        )
    return ExtractedField(value=str(field_data) if field_data else None, confidence=0.5)


def _parse_numeric_field(data: dict, key: str) -> ExtractedNumericField:
    """Parse a numeric field from JSON into ExtractedNumericField."""
    if not data or key not in data:
        return ExtractedNumericField()
    
    def extract_number(val):
        """Extract number from value, handles strings like '30 points' or '0.16'."""
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            # Try to extract first number from string
            import re
            match = re.search(r'[-+]?\d*\.?\d+', val)
            if match:
                return float(match.group())
        return None
    
    field_data = data[key]
    if isinstance(field_data, dict):
        value = extract_number(field_data.get("value"))
        value_range = field_data.get("value_range")
        quote = field_data.get("source_quote")
        if quote and len(quote) > 450:
            quote = quote[:447] + "..."
        return ExtractedNumericField(
            value=value,
            value_range=tuple(value_range) if value_range and isinstance(value_range, list) else None,
            confidence=float(field_data.get("confidence", 0)) if field_data.get("confidence") else 0.0,
            source_quote=quote,
            interpretation=field_data.get("interpretation", "missing"),
        )
    return ExtractedNumericField(value=extract_number(field_data), confidence=0.5)



def _parse_extraction(json_str: str) -> ExtractedStrategy:
    """Parse JSON string into ExtractedStrategy."""
    try:
        # Clean up JSON string (remove markdown code blocks if present)
        clean_json = json_str.strip()
        
        # Remove markdown code blocks
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0]
        elif "```" in clean_json:
            parts = clean_json.split("```")
            if len(parts) >= 2:
                clean_json = parts[1]
        
        clean_json = clean_json.strip()
        
        # Find the JSON object boundaries
        start_idx = clean_json.find('{')
        end_idx = clean_json.rfind('}')
        
        if start_idx == -1 or end_idx == -1:
            raise json.JSONDecodeError("No JSON object found", clean_json, 0)
        
        clean_json = clean_json[start_idx:end_idx + 1]
        
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
        # Log the error for debugging
        print(f"JSON Parse Error: {e}")
        print(f"Raw response (first 500 chars): {json_str[:500] if json_str else 'empty'}")
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
            prompt = build_extraction_prompt(chunk)
            response = await _call_gemini(prompt)
            extraction = _parse_extraction(response)
            chunk_extractions.append(extraction)
        
        # Merge extractions (take highest confidence for each field)
        return _merge_extractions(chunk_extractions)
    else:
        # Single extraction
        prompt = build_extraction_prompt(content)
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
