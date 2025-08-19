from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import yfinance as yf
import logging
import gradio as gr
from langchain_core.tools import tool
import json
from langchain_community.tools import BraveSearch
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

@tool
def get_stock_price(symbol: str) -> str:
    """Get current stock price and basic information."""
    logging.info(f"[TOOL] Fetching stock price for: {symbol}")
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="1d")
        if hist.empty:
            logging.error("No historical data found")
            return json.dumps({"error": f"Could not retrieve data for {symbol}"})

        current_price = hist['Close'].iloc[-1]
        result = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "company_name": info.get('longName', symbol),
            "market_cap": info.get('marketCap', 0),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "52_week_high": info.get('fiftyTwoWeekHigh', 0),
            "52_week_low": info.get('fiftyTwoWeekLow', 0)
        }
        logging.info(f"[TOOL RESULT] {result}")
        return json.dumps(result, indent=2)

    except Exception as e:
        logging.exception("Exception in get_stock_price")
        return json.dumps({"error": str(e)})


@tool
def get_financial_statements(symbol: str) -> str:
    """Retrieve key financial statement data."""
    try:
        stock = yf.Ticker(symbol)
        financials = stock.financials
        balance_sheet = stock.balance_sheet

        latest_year = financials.columns[0]

        return json.dumps(
            {
                "symbol": symbol,
                "period": str(latest_year.year),
                "revenue": (
                    float(financials.loc["Total Revenue", latest_year])
                    if "Total Revenue" in financials.index
                    else "N/A"
                ),
                "net_income": (
                    float(financials.loc["Net Income", latest_year])
                    if "Net Income" in financials.index
                    else "N/A"
                ),
                "total_assets": (
                    float(balance_sheet.loc["Total Assets", latest_year])
                    if "Total Assets" in balance_sheet.index
                    else "N/A"
                ),
                "total_debt": (
                    float(balance_sheet.loc["Total Debt", latest_year])
                    if "Total Debt" in balance_sheet.index
                    else "N/A"
                ),
            },
            indent=2,
        )
    except Exception as e:
        return f"Error: {str(e)}"


brave_search = BraveSearch.from_api_key(
    api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
    search_kwargs={"count": 3}  
)

@tool
def search_financial_news(company_name: str, symbol: str) -> str:
    """Search for recent financial news about a company using Brave Search."""
    try:
        search_query = f"{company_name} {symbol} financial news stock earnings latest"
        results = brave_search.run(search_query)
        
        return json.dumps({
            "symbol": symbol,
            "company": company_name,
            "search_query": search_query,
            "news_results": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to search news: {str(e)}"})


@tool
def search_market_trends(topic: str) -> str:
    """Search for market trends and analysis on a specific topic using Brave Search."""
    try:
        search_query = f"{topic} market analysis trends 2024 2025 investment outlook forecast"
        results = brave_search.run(search_query)
        
        return json.dumps({
            "topic": topic,
            "search_query": search_query,
            "trend_results": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to search trends: {str(e)}"})


@tool
def get_technical_indicators(symbol: str, period: str = "3mo") -> str:
    """Calculate key technical indicators."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            return f"Error: No historical data for {symbol}"

        hist["SMA_20"] = hist["Close"].rolling(window=20).mean()
        hist["SMA_50"] = hist["Close"].rolling(window=50).mean()

        delta = hist["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        latest = hist.iloc[-1]
        latest_rsi = rsi.iloc[-1]

        return json.dumps(
            {
                "symbol": symbol,
                "current_price": round(latest["Close"], 2),
                "sma_20": round(latest["SMA_20"], 2),
                "sma_50": round(latest["SMA_50"], 2),
                "rsi": round(latest_rsi, 2),
                "volume": int(latest["Volume"]),
                "trend_signal": (
                    "bullish"
                    if latest["Close"] > latest["SMA_20"] > latest["SMA_50"]
                    else "bearish"
                ),
            },
            indent=2,
        )
    except Exception as e:
        return f"Error: {str(e)}"


# Sub-agent configurations
fundamental_analyst = {
    "name": "fundamental-analyst",
    "description": "Performs deep fundamental analysis of companies including financial ratios, growth metrics, and valuation",
    "prompt": """You are an expert fundamental analyst with 15+ years of experience. 
    Focus on:
    - Financial statement analysis
    - Ratio analysis (P/E, P/B, ROE, ROA, Debt-to-Equity)
    - Growth metrics and trends
    - Industry comparisons
    - Intrinsic value calculations
    Always provide specific numbers and cite your sources.""",
}

technical_analyst = {
    "name": "technical-analyst",
    "description": "Analyzes price patterns, technical indicators, and trading signals",
    "prompt": """You are a professional technical analyst specializing in chart analysis and trading signals.
    Focus on:
    - Price action and trend analysis
    - Technical indicators (RSI, MACD, Moving Averages)
    - Support and resistance levels
    - Volume analysis
    - Entry/exit recommendations
    Provide specific price levels and timeframes for your recommendations.""",
}

risk_analyst = {
    "name": "risk-analyst",
    "description": "Evaluates investment risks and provides risk assessment",
    "prompt": """You are a risk management specialist focused on identifying and quantifying investment risks.
    Focus on:
    - Market risk analysis
    - Company-specific risks
    - Sector and industry risks
    - Liquidity and credit risks
    - Regulatory and compliance risks
    Always quantify risks where possible and suggest mitigation strategies.""",
}

subagents = [fundamental_analyst, technical_analyst, risk_analyst]


# Main research instructions
research_instructions = """You are an elite stock research analyst with access to multiple specialized tools and sub-agents. 

Your research process should be systematic and comprehensive:

1. **Initial Data Gathering**: Start by collecting basic stock information, price data, and recent news
2. **News & Market Research**: Use Brave Search to find recent financial news and market trends
3. **Fundamental Analysis**: Deep dive into financial statements, ratios, and company fundamentals
4. **Technical Analysis**: Analyze price patterns, trends, and technical indicators
5. **Risk Assessment**: Identify and evaluate potential risks
6. **Competitive Analysis**: Compare with industry peers when relevant
7. **Synthesis**: Combine all findings into a coherent investment thesis
8. **Recommendation**: Provide clear buy/sell/hold recommendation with price targets

Always:
- Use specific data and numbers to support your analysis
- Cite your sources and methodology
- Include recent news and market sentiment in your analysis from Brave Search results
- Consider multiple perspectives and potential scenarios
- Provide actionable insights and concrete recommendations
- Structure your final report professionally

When using sub-agents, provide them with specific, focused tasks and incorporate their specialized insights into your overall analysis."""

_brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
tools = [get_stock_price, get_financial_statements, get_technical_indicators]
if _brave_api_key:
    tools.extend([search_financial_news, search_market_trends])
else:
    logging.info("BRAVE_SEARCH_API_KEY not found: excluding Brave Search tools from tools list")


def run_stock_research(query: str, model_provider: str = "ollama"):
    """Run the stock research agent and return the final message content with debug logging."""
    try:
        logging.info(f"[run_stock_research] Query received: {query}")
        logging.info(f"[run_stock_research] Model provider: {model_provider}")

        # Create model based on selection
        if model_provider == "lm_studio":
            selected_model = ChatOpenAI(
                base_url="http://localhost:1234/v1",
                api_key="lm-studio",
                model="local-model",
                temperature=0,
            )
        else:  # ollama
            selected_model = ChatOllama(
                model="gpt-oss",
                temperature=0,
            )

        # Create agent with selected model
        agent = create_deep_agent(
            tools=tools,
            instructions=research_instructions,
            subagents=subagents,
            model=selected_model,
        )

        result = agent.invoke({"messages": [{"role": "user", "content": query}]})

        logging.debug(f"[run_stock_research] Full result: {result}")

        messages = result.get("messages", [])
        output_text = ""

        if not messages:
            logging.warning("[run_stock_research] No messages returned in result.")
            output_text = "Error: No response messages received."
        elif isinstance(messages[-1], dict):
            output_text = messages[-1].get("content", "")
            logging.debug(f"[run_stock_research] Output content from dict: {output_text}")
        elif hasattr(messages[-1], "content"):
            output_text = messages[-1].content
            logging.debug(f"[run_stock_research] Output content from object: {output_text}")
        else:
            logging.error("[run_stock_research] Unrecognized message format.")
            output_text = "Error: Invalid response message format."

        file_output = ""
        if "files" in result:
            file_output += "\n\n=== Generated Research Files ===\n"
            for filename, content in result["files"].items():
                preview = content[:500] + "..." if len(content) > 500 else content
                file_output += f"\n**{filename}**\n{preview}\n"
                logging.debug(f"[run_stock_research] File: {filename}, Preview: {preview[:100]}")

        return output_text + file_output

    except Exception as e:
        logging.exception("[run_stock_research] Exception during invocation:")
        return f"Error: {str(e)}"


# Create Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 📊 Stock Research Agent with Brave Search")
    gr.Markdown("Enter your stock research request below. Example: *Comprehensive analysis on Apple Inc. (AAPL)*")
    
    # Check if API key is loaded from .env
    env_api_key = os.getenv("BRAVE_SEARCH_API_KEY", "")
    api_status = "✅ API Key loaded from .env" if env_api_key else "❌ No API Key in .env"
    
    gr.Markdown(f"""
    **Brave Search API Setup:**
    1. Get your free API key at [Brave Search API](https://api.search.brave.com/)
    2. Create a `.env` file in this directory with: `BRAVE_SEARCH_API_KEY=your_api_key_here`
    
    **Current Status:** {api_status}
    {f"**Loaded Key:** {env_api_key[:8]}...{env_api_key[-4:]} (masked)" if env_api_key else ""}
    """)

    with gr.Row():
        model_dropdown = gr.Dropdown(
            choices=["ollama", "lm_studio"],
            value="ollama",
            label="Model Provider",
            info="Choose between Ollama (local) or LM Studio (local)",
        )

    with gr.Row():
        query_input = gr.Textbox(label="Research Query", lines=6, placeholder="Type your research query here...")

    run_button = gr.Button("Run Analysis")
    output_box = gr.Textbox(label="Research Report", lines=20)

    run_button.click(fn=run_stock_research, inputs=[query_input, model_dropdown], outputs=output_box)

# Launch app
demo.launch(server_name="0.0.0.0", server_port=7860)
