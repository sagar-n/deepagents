"""Input validation utilities for DeepAgents."""

import re
from typing import List, Optional


def validate_stock_symbol(symbol: str) -> tuple[bool, Optional[str]]:
    """
    Validate stock symbol format.

    Args:
        symbol: Stock ticker symbol to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symbol:
        return False, "Stock symbol cannot be empty"

    # Convert to uppercase
    symbol = symbol.strip().upper()

    # Check length (most stock symbols are 1-5 characters)
    if len(symbol) < 1 or len(symbol) > 5:
        return False, f"Stock symbol must be 1-5 characters, got {len(symbol)}"

    # Check format: letters only, optionally with a dot for special cases
    if not re.match(r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$', symbol):
        return False, f"Invalid stock symbol format: {symbol}. Use uppercase letters only (e.g., AAPL, BRK.B)"

    return True, None


def validate_period(period: str) -> tuple[bool, Optional[str]]:
    """
    Validate time period format for historical data.

    Args:
        period: Time period string (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    if not period:
        return False, "Period cannot be empty"

    if period not in valid_periods:
        return False, f"Invalid period: {period}. Valid periods: {', '.join(valid_periods)}"

    return True, None


def normalize_stock_symbol(symbol: str) -> str:
    """
    Normalize stock symbol to standard format.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Normalized symbol in uppercase
    """
    return symbol.strip().upper()


def validate_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate user research query.

    Args:
        query: User's research query

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query:
        return False, "Query cannot be empty"

    if len(query) < 5:
        return False, "Query too short. Please provide more details about your research request."

    if len(query) > 2000:
        return False, "Query too long. Please limit to 2000 characters."

    return True, None


def extract_symbols_from_query(query: str) -> List[str]:
    """
    Extract potential stock symbols from a query.

    Args:
        query: User's research query

    Returns:
        List of potential stock symbols found in the query
    """
    # Look for patterns like (AAPL) or just uppercase 1-5 letter words
    pattern = r'\b([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\b'
    matches = re.findall(pattern, query)

    # Filter to only include valid symbols
    symbols = []
    for match in matches:
        is_valid, _ = validate_stock_symbol(match)
        if is_valid:
            symbols.append(match)

    return list(set(symbols))  # Remove duplicates
