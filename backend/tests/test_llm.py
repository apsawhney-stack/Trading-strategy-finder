"""
Unit tests for LLM strategy extraction.
Test cases TC-LLM-001 through TC-LLM-005.
"""

import pytest
from app.extractors.llm import _parse_field, _parse_numeric_field, _parse_extraction
from app.models import ExtractedField, ExtractedNumericField


class TestLLMExtraction:
    """Test suite for LLM extraction utilities."""

    # TC-LLM-001: Parse explicit field
    def test_parse_field_explicit(self):
        """Test parsing an explicit field."""
        data = {
            "strategy_name": {
                "value": "Put Credit Spread",
                "confidence": 0.95,
                "source_quote": "I trade put credit spreads",
                "interpretation": "explicit"
            }
        }
        field = _parse_field(data, "strategy_name")
        assert field.value == "Put Credit Spread"
        assert field.confidence == 0.95
        assert field.interpretation == "explicit"

    # TC-LLM-002: Parse implicit field
    def test_parse_field_implicit(self):
        """Test parsing an implicit field."""
        data = {
            "dte": {
                "value": "7",
                "confidence": 0.8,
                "source_quote": "weekly options",
                "interpretation": "implicit"
            }
        }
        field = _parse_field(data, "dte")
        assert field.value == "7"
        assert field.confidence == 0.8
        assert field.interpretation == "implicit"

    # TC-LLM-003: Parse missing field
    def test_parse_field_missing(self):
        """Test parsing when field is missing."""
        data = {}
        field = _parse_field(data, "nonexistent")
        assert field.value is None
        assert field.confidence == 0.0
        assert field.interpretation == "missing"

    # TC-LLM-004: Parse numeric field with range
    def test_parse_numeric_field_with_range(self):
        """Test parsing numeric field with value range."""
        data = {
            "dte": {
                "value": 30,
                "value_range": [25, 45],
                "confidence": 0.9,
                "interpretation": "explicit"
            }
        }
        field = _parse_numeric_field(data, "dte")
        assert field.value == 30.0
        assert field.value_range == (25, 45)
        assert field.confidence == 0.9

    # TC-LLM-005: Parse full extraction JSON
    def test_parse_extraction_full(self):
        """Test parsing complete extraction JSON."""
        json_str = '''
        {
            "strategy_name": {"value": "Iron Condor", "confidence": 0.9, "interpretation": "explicit"},
            "setup_rules": {
                "underlying": {"value": "SPY", "confidence": 0.9, "interpretation": "explicit"},
                "dte": {"value": 45, "confidence": 0.8, "interpretation": "explicit"}
            },
            "failure_analysis": {
                "failure_modes_mentioned": ["gap risk"],
                "discusses_losses": true,
                "bias_detected": false
            },
            "key_insights": ["Sell premium in high IV"],
            "warnings": ["Not for trending markets"]
        }
        '''
        extraction = _parse_extraction(json_str)
        assert extraction.strategy_name.value == "Iron Condor"
        assert extraction.setup_rules.underlying.value == "SPY"
        assert len(extraction.failure_analysis.failure_modes_mentioned) == 1
        assert len(extraction.key_insights) == 1

    def test_parse_extraction_invalid_json(self):
        """Test that invalid JSON returns empty extraction."""
        json_str = "not valid json {"
        extraction = _parse_extraction(json_str)
        assert extraction.strategy_name.value is None

    def test_parse_extraction_with_markdown(self):
        """Test parsing JSON wrapped in markdown code block."""
        json_str = '''```json
        {"strategy_name": {"value": "Wheel", "confidence": 0.9, "interpretation": "explicit"}}
        ```'''
        extraction = _parse_extraction(json_str)
        assert extraction.strategy_name.value == "Wheel"
