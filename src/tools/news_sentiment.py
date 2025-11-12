"""News and sentiment analysis tool."""

import logging
import json
from datetime import datetime
import yfinance as yf
from langchain_core.tools import tool

from ..utils.validation import validate_stock_symbol, normalize_stock_symbol
from ..utils.cache import cached, get_stock_price_cache
from ..utils.retry import exponential_backoff_retry

logger = logging.getLogger(__name__)


@cached(get_stock_price_cache())
@exponential_backoff_retry(exceptions=(Exception,))
def _fetch_news_sentiment(symbol: str, max_articles: int = 5) -> dict:
    """
    Internal function to fetch news and perform basic sentiment analysis.

    Args:
        symbol: Stock ticker symbol
        max_articles: Maximum number of recent articles to retrieve

    Returns:
        Dictionary with news articles and basic sentiment
    """
    stock = yf.Ticker(symbol)
    news = stock.news

    if not news:
        return {
            "symbol": symbol,
            "articles_count": 0,
            "message": f"No recent news found for {symbol}"
        }

    # Limit to max_articles
    news = news[:max_articles]

    articles = []
    for item in news:
        # Extract relevant information
        article = {
            "title": item.get('title', 'N/A'),
            "publisher": item.get('publisher', 'Unknown'),
            "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S'),
            "link": item.get('link', 'N/A')
        }

        # Basic sentiment analysis based on keywords in title
        title_lower = article['title'].lower()
        positive_keywords = ['up', 'surge', 'gain', 'beat', 'strong', 'growth', 'profit', 'rise', 'bullish', 'outperform', 'upgrade']
        negative_keywords = ['down', 'fall', 'loss', 'miss', 'weak', 'decline', 'drop', 'bearish', 'underperform', 'downgrade']

        positive_count = sum(1 for word in positive_keywords if word in title_lower)
        negative_count = sum(1 for word in negative_keywords if word in title_lower)

        if positive_count > negative_count:
            article['sentiment'] = 'positive'
        elif negative_count > positive_count:
            article['sentiment'] = 'negative'
        else:
            article['sentiment'] = 'neutral'

        articles.append(article)

    # Calculate overall sentiment
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for article in articles:
        sentiment_counts[article['sentiment']] += 1

    total = len(articles)
    overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)

    return {
        "symbol": symbol,
        "articles_count": total,
        "overall_sentiment": overall_sentiment,
        "sentiment_breakdown": {
            "positive": f"{(sentiment_counts['positive'] / total * 100):.1f}%",
            "negative": f"{(sentiment_counts['negative'] / total * 100):.1f}%",
            "neutral": f"{(sentiment_counts['neutral'] / total * 100):.1f}%"
        },
        "recent_articles": articles
    }


@tool
def get_news_sentiment(symbol: str, max_articles: int = 5) -> str:
    """
    Get recent news articles and sentiment analysis for a stock.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        max_articles: Maximum number of recent articles to analyze (default: 5)

    Returns:
        JSON string with recent news articles, individual sentiment scores,
        and overall sentiment breakdown (positive/negative/neutral)
    """
    logger.info(f"[TOOL] Fetching news sentiment for: {symbol}")

    # Validate and normalize symbol
    symbol = normalize_stock_symbol(symbol)
    is_valid, error_msg = validate_stock_symbol(symbol)

    if not is_valid:
        logger.error(f"[TOOL ERROR] Invalid symbol: {error_msg}")
        return json.dumps({"error": error_msg})

    try:
        result = _fetch_news_sentiment(symbol, max_articles)
        logger.info(f"[TOOL RESULT] Successfully fetched news for {symbol}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.exception(f"[TOOL ERROR] Unexpected error fetching news for {symbol}")
        return json.dumps({"error": f"Failed to retrieve news for {symbol}: {str(e)}"})
