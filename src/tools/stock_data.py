"""Stock price data retrieval tool."""

import logging
import json
import yfinance as yf
from langchain_core.tools import tool

from ..utils.validation import validate_stock_symbol, normalize_stock_symbol
from ..utils.cache import cached, get_stock_price_cache
from ..utils.retry import exponential_backoff_retry

logger = logging.getLogger(__name__)


@cached(get_stock_price_cache())
@exponential_backoff_retry(exceptions=(Exception,))
def _fetch_stock_price(symbol: str) -> dict:
    """
    Internal function to fetch stock price (with caching and retry).

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with stock price data
    """
    stock = yf.Ticker(symbol)
    info = stock.info
    hist = stock.history(period="1d")

    if hist.empty:
        raise ValueError(f"No historical data found for {symbol}")

    current_price = hist['Close'].iloc[-1]

    return {
        "symbol": symbol,
        "current_price": round(current_price, 2),
        "company_name": info.get('longName', symbol),
        "market_cap": info.get('marketCap', 0),
        "pe_ratio": info.get('trailingPE', 'N/A'),
        "52_week_high": info.get('fiftyTwoWeekHigh', 0),
        "52_week_low": info.get('fiftyTwoWeekLow', 0),
        "volume": info.get('volume', 0),
        "avg_volume": info.get('averageVolume', 0),
        "dividend_yield": info.get('dividendYield', 0)
    }


@tool
def get_stock_price(symbol: str) -> str:
    """
    Get current stock price and basic information.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        JSON string with stock price and company information
    """
    logger.info(f"[TOOL] Fetching stock price for: {symbol}")

    # Validate and normalize symbol
    symbol = normalize_stock_symbol(symbol)
    is_valid, error_msg = validate_stock_symbol(symbol)

    if not is_valid:
        logger.error(f"[TOOL ERROR] Invalid symbol: {error_msg}")
        return json.dumps({"error": error_msg})

    try:
        result = _fetch_stock_price(symbol)
        logger.info(f"[TOOL RESULT] Successfully fetched data for {symbol}")
        return json.dumps(result, indent=2)

    except ValueError as e:
        logger.error(f"[TOOL ERROR] Data error: {str(e)}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception(f"[TOOL ERROR] Unexpected error fetching {symbol}")
        return json.dumps({"error": f"Failed to retrieve data for {symbol}: {str(e)}"})
