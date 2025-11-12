"""Technical indicators calculation tool."""

import logging
import json
import yfinance as yf
from langchain_core.tools import tool

from ..utils.validation import validate_stock_symbol, normalize_stock_symbol, validate_period
from ..utils.cache import cached, get_technical_cache
from ..utils.retry import exponential_backoff_retry
from ..utils.config import settings

logger = logging.getLogger(__name__)


@cached(get_technical_cache())
@exponential_backoff_retry(exceptions=(Exception,))
def _fetch_technical_indicators(symbol: str, period: str = "3mo") -> dict:
    """
    Internal function to fetch and calculate technical indicators (with caching and retry).

    Args:
        symbol: Stock ticker symbol
        period: Historical data period

    Returns:
        Dictionary with technical indicator data
    """
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)

    if hist.empty:
        raise ValueError(f"No historical data found for {symbol}")

    # Calculate moving averages
    hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
    hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
    hist['SMA_200'] = hist['Close'].rolling(window=200).mean()

    # Calculate RSI (Relative Strength Index)
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Calculate MACD
    ema_12 = hist['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = hist['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal_line = macd.ewm(span=9, adjust=False).mean()

    # Get latest values
    latest = hist.iloc[-1]
    latest_rsi = rsi.iloc[-1]
    latest_macd = macd.iloc[-1]
    latest_signal = signal_line.iloc[-1]

    # Determine trend signals
    price = latest['Close']
    sma_20 = latest['SMA_20']
    sma_50 = latest['SMA_50']

    if price > sma_20 > sma_50:
        trend_signal = "strong_bullish"
    elif price > sma_20:
        trend_signal = "bullish"
    elif price < sma_20 < sma_50:
        trend_signal = "strong_bearish"
    elif price < sma_20:
        trend_signal = "bearish"
    else:
        trend_signal = "neutral"

    # RSI signals
    if latest_rsi > 70:
        rsi_signal = "overbought"
    elif latest_rsi < 30:
        rsi_signal = "oversold"
    else:
        rsi_signal = "neutral"

    # MACD signal
    macd_signal = "bullish" if latest_macd > latest_signal else "bearish"

    return {
        "symbol": symbol,
        "period": period,
        "current_price": round(price, 2),
        "sma_20": round(sma_20, 2) if not pd.isna(sma_20) else None,
        "sma_50": round(sma_50, 2) if not pd.isna(sma_50) else None,
        "sma_200": round(latest['SMA_200'], 2) if not pd.isna(latest['SMA_200']) else None,
        "rsi": round(latest_rsi, 2) if not pd.isna(latest_rsi) else None,
        "rsi_signal": rsi_signal,
        "macd": round(latest_macd, 2) if not pd.isna(latest_macd) else None,
        "macd_signal_line": round(latest_signal, 2) if not pd.isna(latest_signal) else None,
        "macd_signal": macd_signal,
        "volume": int(latest['Volume']),
        "avg_volume_20d": int(hist['Volume'].tail(20).mean()),
        "trend_signal": trend_signal,
        "52_week_high": round(hist['Close'].max(), 2),
        "52_week_low": round(hist['Close'].min(), 2)
    }


# Import pandas for isna checks
import pandas as pd


@tool
def get_technical_indicators(symbol: str, period: str = None) -> str:
    """
    Calculate key technical indicators for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        period: Historical data period (default: 3mo)
                Valid: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    Returns:
        JSON string with technical indicators including moving averages (SMA 20/50/200),
        RSI, MACD, volume analysis, and trend signals
    """
    logger.info(f"[TOOL] Calculating technical indicators for: {symbol}, period: {period}")

    # Use default period if not specified
    if period is None:
        period = settings.DEFAULT_HISTORY_PERIOD

    # Validate and normalize symbol
    symbol = normalize_stock_symbol(symbol)
    is_valid, error_msg = validate_stock_symbol(symbol)

    if not is_valid:
        logger.error(f"[TOOL ERROR] Invalid symbol: {error_msg}")
        return json.dumps({"error": error_msg})

    # Validate period
    is_valid_period, period_error = validate_period(period)
    if not is_valid_period:
        logger.error(f"[TOOL ERROR] Invalid period: {period_error}")
        return json.dumps({"error": period_error})

    try:
        result = _fetch_technical_indicators(symbol, period)
        logger.info(f"[TOOL RESULT] Successfully calculated indicators for {symbol}")
        return json.dumps(result, indent=2)

    except ValueError as e:
        logger.error(f"[TOOL ERROR] Data error: {str(e)}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception(f"[TOOL ERROR] Unexpected error calculating indicators for {symbol}")
        return json.dumps({"error": f"Failed to calculate indicators for {symbol}: {str(e)}"})
