#!/usr/bin/env python3
"""
Extended POC: YouTube Transcript → Strategy Extraction
Uses Gemini API to extract structured strategy data from video transcripts.
"""

import json
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Check for google.generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Install with: pip install google-generativeai")

VIDEO_ID = "55ox9fB3x-E"

# Strategy extraction prompt template
EXTRACTION_PROMPT = """You are an expert options trading analyst. Analyze the following YouTube video transcript and extract structured information about the trading strategy discussed.

VIDEO TRANSCRIPT:
---
{transcript}
---

Extract the following information in JSON format. If information is not mentioned, use null.

{{
  "strategy_overview": {{
    "name": "Name of the strategy (e.g., 'ATM Put Credit Spreads on SPX')",
    "one_liner": "One sentence summary of the strategy",
    "trader_name": "Name of the trader being interviewed, if mentioned",
    "experience_level": "How long they've been trading this strategy"
  }},
  "setup_rules": {{
    "underlying": "What they trade (e.g., SPX, SPY, individual stocks)",
    "option_type": "Type of options (puts, calls, spreads, etc.)",
    "strike_selection": "How they choose strikes (ATM, OTM, delta-based, etc.)",
    "expiration": "DTE (days to expiration) they typically use",
    "position_sizing": "How they size positions relative to account",
    "entry_criteria": "What conditions trigger an entry",
    "time_of_day": "When they typically enter trades"
  }},
  "management_rules": {{
    "profit_target": "When they take profits (e.g., 50% of credit)",
    "stop_loss": "When they cut losses",
    "adjustment_rules": "How they adjust losing trades",
    "hold_to_expiration": "Do they let positions expire or close early?",
    "rolling_rules": "Do they roll positions? When?"
  }},
  "risk_profile": {{
    "max_loss_per_trade": "Maximum loss on a single trade",
    "win_rate_claimed": "Win rate mentioned by trader",
    "risk_reward_ratio": "Typical risk to reward",
    "account_drawdown_mentioned": "Any drawdowns or losing streaks mentioned"
  }},
  "performance_claims": {{
    "starting_capital": "Initial account size",
    "current_capital": "Current account size",
    "total_return_percent": "Percentage return claimed",
    "time_period": "Over what time period",
    "profits_withdrawn": "Any profits taken out"
  }},
  "key_insights": [
    "List of unique insights or tips mentioned",
    "Things the trader does differently",
    "Lessons learned"
  ],
  "warnings_and_risks": [
    "Any risks or warnings mentioned",
    "What could go wrong",
    "Market conditions where this fails"
  ],
  "quotes": [
    "Notable direct quotes from the transcript that capture key ideas"
  ]
}}

Return ONLY valid JSON, no markdown formatting or explanation.
"""


def fetch_transcript(video_id):
    """Fetch transcript for a YouTube video."""
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        transcript_data = list(fetched)
        full_text = " ".join([entry.text for entry in transcript_data])
        return full_text, transcript_data
    except Exception as e:
        print(f"❌ Failed to fetch transcript: {e}")
        return None, None


def extract_strategy_with_gemini(transcript_text, api_key=None):
    """Use Gemini to extract structured strategy data."""
    if not GEMINI_AVAILABLE:
        return None
    
    # Configure API
    api_key = api_key or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No Gemini API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable.")
        return None
    
    genai.configure(api_key=api_key)
    
    # Try multiple models in order of preference
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.5-pro', 
        'gemini-2.0-flash-lite',
        'gemini-flash-latest',
    ]
    
    prompt = EXTRACTION_PROMPT.format(transcript=transcript_text[:30000])  # Limit context
    
    for model_name in models_to_try:
        print(f"🤖 Trying model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response - remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n?', '', response_text)
                response_text = re.sub(r'\n?```$', '', response_text)
            
            # Parse JSON
            extracted = json.loads(response_text)
            print(f"✅ Success with {model_name}!")
            return extracted
        except json.JSONDecodeError as e:
            print(f"❌ {model_name}: Failed to parse JSON: {e}")
            continue
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                print(f"⚠️ {model_name}: Rate limited, trying next model...")
                continue
            else:
                print(f"❌ {model_name}: Error - {e}")
                continue
    
    print("❌ All models failed or rate limited")
    return None


def extract_strategy_rule_based(transcript_text):
    """Fallback: Extract strategy data using rule-based parsing (no LLM needed)."""
    extracted = {
        "strategy_overview": {
            "name": None,
            "one_liner": None,
            "trader_name": None,
            "experience_level": None
        },
        "setup_rules": {},
        "management_rules": {},
        "risk_profile": {},
        "performance_claims": {},
        "key_insights": [],
        "warnings_and_risks": [],
        "quotes": []
    }
    
    text_lower = transcript_text.lower()
    
    # Detect strategy type
    if "credit spread" in text_lower:
        extracted["strategy_overview"]["name"] = "Credit Spreads"
    if "put credit spread" in text_lower:
        extracted["strategy_overview"]["name"] = "Put Credit Spreads"
    if "iron condor" in text_lower:
        extracted["strategy_overview"]["name"] = "Iron Condor"
    if "wheel" in text_lower:
        extracted["strategy_overview"]["name"] = "Wheel Strategy"
    
    # Detect underlying
    if "s&p" in text_lower or "spx" in text_lower or "spy" in text_lower:
        extracted["setup_rules"]["underlying"] = "S&P 500 (SPX/SPY)"
    
    # Detect strike selection
    if "at the money" in text_lower or "atm" in text_lower:
        extracted["setup_rules"]["strike_selection"] = "At The Money (ATM)"
    elif "out of the money" in text_lower or "otm" in text_lower:
        extracted["setup_rules"]["strike_selection"] = "Out of The Money (OTM)"
    
    # Detect DTE
    dte_patterns = [
        r'(\d+)\s*(?:day|dte)',
        r'(\d+)\s*days?\s*(?:to|until)\s*expir',
        r'expire\s*(?:in|within)\s*(\d+)'
    ]
    for pattern in dte_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted["setup_rules"]["expiration"] = f"{match.group(1)} DTE"
            break
    
    # Detect profit target
    profit_patterns = [
        r'(\d+)%?\s*(?:of\s*)?(?:credit|premium)',
        r'take\s*profit\s*(?:at\s*)?(\d+)',
        r'close\s*(?:at\s*)?(\d+)%'
    ]
    for pattern in profit_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted["management_rules"]["profit_target"] = f"{match.group(1)}% of credit"
            break
    
    # Extract dollar amounts for performance
    dollar_pattern = r'\$([0-9,]+(?:\.\d{2})?)'
    amounts = re.findall(dollar_pattern, transcript_text)
    if len(amounts) >= 2:
        amounts_cleaned = [int(a.replace(',', '').split('.')[0]) for a in amounts]
        amounts_cleaned = sorted(set(amounts_cleaned))
        if len(amounts_cleaned) >= 2:
            extracted["performance_claims"]["starting_capital"] = f"${amounts_cleaned[0]:,}"
            extracted["performance_claims"]["current_capital"] = f"${amounts_cleaned[-1]:,}"
    
    return extracted


def display_results(extracted):
    """Pretty print the extracted strategy data."""
    print("\n" + "=" * 70)
    print("📊 EXTRACTED STRATEGY DATA")
    print("=" * 70)
    
    # Overview
    overview = extracted.get("strategy_overview", {})
    if overview.get("name"):
        print(f"\n🎯 Strategy: {overview['name']}")
    if overview.get("one_liner"):
        print(f"   Summary: {overview['one_liner']}")
    if overview.get("trader_name"):
        print(f"   Trader: {overview['trader_name']}")
    
    # Setup Rules
    setup = extracted.get("setup_rules", {})
    if any(setup.values()):
        print("\n📋 SETUP RULES:")
        for key, value in setup.items():
            if value:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Management Rules
    mgmt = extracted.get("management_rules", {})
    if any(mgmt.values()):
        print("\n⚙️ MANAGEMENT RULES:")
        for key, value in mgmt.items():
            if value:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Performance
    perf = extracted.get("performance_claims", {})
    if any(perf.values()):
        print("\n📈 PERFORMANCE CLAIMS:")
        for key, value in perf.items():
            if value:
                print(f"   • {key.replace('_', ' ').title()}: {value}")
    
    # Key Insights
    insights = extracted.get("key_insights", [])
    if insights:
        print("\n💡 KEY INSIGHTS:")
        for insight in insights[:5]:
            print(f"   • {insight}")
    
    # Warnings
    warnings = extracted.get("warnings_and_risks", [])
    if warnings:
        print("\n⚠️ WARNINGS & RISKS:")
        for warning in warnings[:5]:
            print(f"   • {warning}")
    
    # Notable Quotes
    quotes = extracted.get("quotes", [])
    if quotes:
        print("\n💬 NOTABLE QUOTES:")
        for quote in quotes[:3]:
            print(f'   "{quote}"')
    
    print("\n" + "=" * 70)


def main():
    print(f"🎬 Extended POC: YouTube → Strategy Extraction")
    print(f"📹 Video: https://youtu.be/{VIDEO_ID}\n")
    
    # Step 1: Fetch transcript
    print("Step 1: Fetching transcript...")
    transcript_text, segments = fetch_transcript(VIDEO_ID)
    
    if not transcript_text:
        print("❌ Failed to fetch transcript. Exiting.")
        return
    
    print(f"✅ Got {len(transcript_text)} characters\n")
    
    # Step 2: Extract with Gemini (or fallback)
    print("Step 2: Extracting strategy data...")
    
    if GEMINI_AVAILABLE:
        extracted = extract_strategy_with_gemini(transcript_text)
        if extracted:
            print("✅ Gemini extraction successful!")
        else:
            print("⚠️ Gemini failed, using rule-based fallback...")
            extracted = extract_strategy_rule_based(transcript_text)
    else:
        print("⚠️ Gemini not available, using rule-based extraction...")
        extracted = extract_strategy_rule_based(transcript_text)
    
    # Step 3: Display results
    display_results(extracted)
    
    # Step 4: Save to file
    output = {
        "video_id": VIDEO_ID,
        "video_url": f"https://youtu.be/{VIDEO_ID}",
        "transcript_length": len(transcript_text),
        "extraction_method": "gemini" if GEMINI_AVAILABLE else "rule-based",
        "extracted_data": extracted
    }
    
    with open("strategy_extraction_output.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Full extraction saved to: strategy_extraction_output.json")


if __name__ == "__main__":
    main()
