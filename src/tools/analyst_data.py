"""Analyst recommendations and ratings tool."""

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
def _fetch_analyst_recommendations(symbol: str) -> dict:
    """
    Internal function to fetch analyst recommendations and price targets.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with analyst recommendation data
    """
    stock = yf.Ticker(symbol)
    info = stock.info
    recommendations = stock.recommendations

    result = {
        "symbol": symbol,
        "current_price": info.get('currentPrice', 'N/A'),
        "target_mean_price": info.get('targetMeanPrice', 'N/A'),
        "target_high_price": info.get('targetHighPrice', 'N/A'),
        "target_low_price": info.get('targetLowPrice', 'N/A'),
        "number_of_analyst_opinions": info.get('numberOfAnalystOpinions', 0),
        "recommendation_mean": info.get('recommendationMean', 'N/A'),
        "recommendation_key": info.get('recommendationKey', 'N/A')
    }

    # Calculate upside potential
    if result['current_price'] != 'N/A' and result['target_mean_price'] != 'N/A':
        current = float(result['current_price'])
        target = float(result['target_mean_price'])
        upside = ((target - current) / current) * 100
        result['upside_potential'] = f"{upside:.2f}%"

    # Process recent recommendations if available
    if recommendations is not None and not recommendations.empty:
        # Get most recent recommendations (last 10)
        recent_recs = recommendations.tail(10)

        # Count recommendation types
        rec_counts = recent_recs['To Grade'].value_counts().to_dict()

        result['recent_recommendations'] = {
            'count': len(recent_recs),
            'breakdown': rec_counts,
            'latest': {
                'firm': recent_recs.iloc[-1].get('Firm', 'Unknown'),
                'grade': recent_recs.iloc[-1].get('To Grade', 'Unknown'),
                'date': str(recent_recs.index[-1].date()) if hasattr(recent_recs.index[-1], 'date') else 'Unknown'
            }
        }

    # Interpret recommendation mean (1=Strong Buy, 5=Sell)
    if result['recommendation_mean'] != 'N/A':
        mean = float(result['recommendation_mean'])
        if mean <= 1.5:
            result['recommendation_interpretation'] = 'Strong Buy'
        elif mean <= 2.5:
            result['recommendation_interpretation'] = 'Buy'
        elif mean <= 3.5:
            result['recommendation_interpretation'] = 'Hold'
        elif mean <= 4.5:
            result['recommendation_interpretation'] = 'Sell'
        else:
            result['recommendation_interpretation'] = 'Strong Sell'

    return result


@tool
def get_analyst_recommendations(symbol: str) -> str:
    """
    Get analyst recommendations, ratings, and price targets for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        JSON string with analyst data including:
        - Price targets (mean, high, low)
        - Recommendation ratings (buy/hold/sell)
        - Number of analysts covering the stock
        - Recent recommendation changes
        - Upside/downside potential
    """
    logger.info(f"[TOOL] Fetching analyst recommendations for: {symbol}")

    # Validate and normalize symbol
    symbol = normalize_stock_symbol(symbol)
    is_valid, error_msg = validate_stock_symbol(symbol)

    if not is_valid:
        logger.error(f"[TOOL ERROR] Invalid symbol: {error_msg}")
        return json.dumps({"error": error_msg})

    try:
        result = _fetch_analyst_recommendations(symbol)
        logger.info(f"[TOOL RESULT] Successfully fetched analyst data for {symbol}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.exception(f"[TOOL ERROR] Unexpected error fetching analyst data for {symbol}")
        return json.dumps({"error": f"Failed to retrieve analyst data for {symbol}: {str(e)}"})
