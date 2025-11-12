"""Financial statements data retrieval tool."""

import logging
import json
import yfinance as yf
from langchain_core.tools import tool

from ..utils.validation import validate_stock_symbol, normalize_stock_symbol
from ..utils.cache import cached, get_financials_cache
from ..utils.retry import exponential_backoff_retry

logger = logging.getLogger(__name__)


@cached(get_financials_cache())
@exponential_backoff_retry(exceptions=(Exception,))
def _fetch_financial_statements(symbol: str) -> dict:
    """
    Internal function to fetch financial statements (with caching and retry).

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with financial statement data
    """
    stock = yf.Ticker(symbol)
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow

    if financials.empty:
        raise ValueError(f"No financial data found for {symbol}")

    latest_year = financials.columns[0]

    # Helper function to safely get values
    def safe_get(df, key, column):
        try:
            if key in df.index:
                value = df.loc[key, column]
                return float(value) if value is not None else None
            return None
        except:
            return None

    result = {
        "symbol": symbol,
        "period": str(latest_year.year) if hasattr(latest_year, 'year') else str(latest_year),
        "revenue": safe_get(financials, 'Total Revenue', latest_year),
        "net_income": safe_get(financials, 'Net Income', latest_year),
        "operating_income": safe_get(financials, 'Operating Income', latest_year),
        "gross_profit": safe_get(financials, 'Gross Profit', latest_year),
        "total_assets": safe_get(balance_sheet, 'Total Assets', latest_year),
        "total_debt": safe_get(balance_sheet, 'Total Debt', latest_year),
        "total_equity": safe_get(balance_sheet, 'Stockholders Equity', latest_year),
        "cash": safe_get(balance_sheet, 'Cash And Cash Equivalents', latest_year),
        "operating_cashflow": safe_get(cashflow, 'Operating Cash Flow', latest_year),
        "free_cashflow": safe_get(cashflow, 'Free Cash Flow', latest_year)
    }

    # Calculate some key ratios
    if result['revenue'] and result['net_income']:
        result['profit_margin'] = round((result['net_income'] / result['revenue']) * 100, 2)

    if result['total_assets'] and result['net_income']:
        result['roa'] = round((result['net_income'] / result['total_assets']) * 100, 2)

    if result['total_equity'] and result['net_income']:
        result['roe'] = round((result['net_income'] / result['total_equity']) * 100, 2)

    if result['total_debt'] and result['total_equity']:
        result['debt_to_equity'] = round(result['total_debt'] / result['total_equity'], 2)

    return result


@tool
def get_financial_statements(symbol: str) -> str:
    """
    Retrieve key financial statement data and calculated ratios.

    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)

    Returns:
        JSON string with financial statement data including revenue, net income,
        assets, debt, and calculated ratios (profit margin, ROA, ROE, debt-to-equity)
    """
    logger.info(f"[TOOL] Fetching financial statements for: {symbol}")

    # Validate and normalize symbol
    symbol = normalize_stock_symbol(symbol)
    is_valid, error_msg = validate_stock_symbol(symbol)

    if not is_valid:
        logger.error(f"[TOOL ERROR] Invalid symbol: {error_msg}")
        return json.dumps({"error": error_msg})

    try:
        result = _fetch_financial_statements(symbol)
        logger.info(f"[TOOL RESULT] Successfully fetched financials for {symbol}")
        return json.dumps(result, indent=2)

    except ValueError as e:
        logger.error(f"[TOOL ERROR] Data error: {str(e)}")
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception(f"[TOOL ERROR] Unexpected error fetching financials for {symbol}")
        return json.dumps({"error": f"Failed to retrieve financial data for {symbol}: {str(e)}"})
