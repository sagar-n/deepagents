"""Unit tests for validation utilities."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.validation import (
    validate_stock_symbol,
    validate_period,
    normalize_stock_symbol,
    validate_query,
    extract_symbols_from_query
)


class TestStockSymbolValidation:
    """Test stock symbol validation."""

    def test_valid_symbols(self):
        """Test valid stock symbols."""
        assert validate_stock_symbol("AAPL") == (True, None)
        assert validate_stock_symbol("MSFT") == (True, None)
        assert validate_stock_symbol("BRK.B") == (True, None)
        assert validate_stock_symbol("A") == (True, None)

    def test_invalid_symbols(self):
        """Test invalid stock symbols."""
        is_valid, error = validate_stock_symbol("")
        assert not is_valid
        assert "cannot be empty" in error

        is_valid, error = validate_stock_symbol("TOOLONG")
        assert not is_valid
        assert "1-5 characters" in error

        is_valid, error = validate_stock_symbol("123")
        assert not is_valid
        assert "Invalid" in error

    def test_normalize_symbol(self):
        """Test symbol normalization."""
        assert normalize_stock_symbol("aapl") == "AAPL"
        assert normalize_stock_symbol(" msft ") == "MSFT"
        assert normalize_stock_symbol("BRK.B") == "BRK.B"


class TestPeriodValidation:
    """Test period validation."""

    def test_valid_periods(self):
        """Test valid period strings."""
        assert validate_period("1d") == (True, None)
        assert validate_period("3mo") == (True, None)
        assert validate_period("1y") == (True, None)
        assert validate_period("max") == (True, None)

    def test_invalid_periods(self):
        """Test invalid period strings."""
        is_valid, error = validate_period("")
        assert not is_valid

        is_valid, error = validate_period("invalid")
        assert not is_valid
        assert "Invalid period" in error


class TestQueryValidation:
    """Test query validation."""

    def test_valid_queries(self):
        """Test valid queries."""
        assert validate_query("Analyze AAPL stock") == (True, None)
        assert validate_query("What are the risks of investing in Tesla?") == (True, None)

    def test_invalid_queries(self):
        """Test invalid queries."""
        is_valid, error = validate_query("")
        assert not is_valid
        assert "cannot be empty" in error

        is_valid, error = validate_query("Hi")
        assert not is_valid
        assert "too short" in error

        is_valid, error = validate_query("x" * 2001)
        assert not is_valid
        assert "too long" in error


class TestSymbolExtraction:
    """Test symbol extraction from queries."""

    def test_extract_symbols(self):
        """Test extracting symbols from text."""
        symbols = extract_symbols_from_query("Analyze AAPL and MSFT")
        assert "AAPL" in symbols
        assert "MSFT" in symbols

        symbols = extract_symbols_from_query("Compare (GOOGL) vs (AMZN)")
        assert "GOOGL" in symbols
        assert "AMZN" in symbols

    def test_no_symbols(self):
        """Test queries with no valid symbols."""
        symbols = extract_symbols_from_query("What is the stock market?")
        assert len(symbols) == 0
