"""Main entry point for DeepAgents Stock Research Assistant."""

import logging
from deepagents import create_deep_agent
from langchain_ollama import ChatOllama

from .tools import (
    get_stock_price,
    get_financial_statements,
    get_technical_indicators,
    get_news_sentiment,
    get_analyst_recommendations
)
from .agents import fundamental_analyst, technical_analyst, risk_analyst
from .ui import create_gradio_interface
from .utils.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Research instructions for the main agent
RESEARCH_INSTRUCTIONS = """You are an elite stock research analyst with access to multiple specialized tools and sub-agents.

Your research process should be systematic and comprehensive:

1. **Initial Data Gathering**: Start by collecting basic stock information, current price, and recent news
   - Use get_stock_price for current market data
   - Use get_news_sentiment to understand recent market sentiment

2. **Fundamental Analysis**: Deep dive into financial statements, ratios, and company fundamentals
   - Use get_financial_statements for detailed financial data
   - Delegate to the fundamental-analyst sub-agent for in-depth analysis
   - Use get_analyst_recommendations to see what Wall Street thinks

3. **Technical Analysis**: Analyze price patterns, trends, and technical indicators
   - Use get_technical_indicators for chart data and signals
   - Delegate to the technical-analyst sub-agent for pattern analysis and trading signals

4. **Risk Assessment**: Identify and evaluate potential risks
   - Delegate to the risk-analyst sub-agent for comprehensive risk evaluation
   - Consider market, company-specific, and sector risks

5. **Synthesis**: Combine all findings into a coherent investment thesis
   - Reconcile fundamental value with technical signals
   - Balance opportunities against risks
   - Consider multiple perspectives and timeframes

6. **Recommendation**: Provide clear, actionable investment recommendation
   - Buy/Hold/Sell recommendation with confidence level
   - Price targets (12-month outlook)
   - Key catalysts and risk factors to monitor
   - Suggested position sizing based on risk profile

**Guidelines:**
- Always use specific data and numbers to support your analysis
- Cite your sources and methodology
- Consider multiple perspectives and potential scenarios
- Provide actionable insights with concrete entry/exit levels
- Structure your final report professionally with clear sections
- Be objective and balanced - acknowledge both bullish and bearish factors
- When using sub-agents, provide them with specific, focused tasks
- Incorporate specialized insights into your overall analysis
- If data is unavailable, note limitations rather than speculate

**Report Structure:**
Your final report should include:
1. Executive Summary (recommendation, price target, key thesis)
2. Company Overview (from stock data and news)
3. Fundamental Analysis (financials, valuation, analyst views)
4. Technical Analysis (trends, signals, key levels)
5. Risk Assessment (key risks and mitigation)
6. Investment Recommendation (specific action with timeframe)
7. Monitoring Plan (what to watch going forward)

Remember: Provide value through synthesis and insight, not just data aggregation."""


def create_research_agent():
    """
    Create and configure the DeepAgent research system.

    Returns:
        Configured DeepAgent instance
    """
    logger.info("Initializing DeepAgents Stock Research Assistant")

    # Validate configuration
    if not settings.validate():
        raise ValueError("Invalid configuration settings")

    # Create LLM model
    logger.info(f"Loading model: {settings.OLLAMA_MODEL}")
    ollama_model = ChatOllama(
        model=settings.OLLAMA_MODEL,
        temperature=settings.TEMPERATURE,
    )

    # Define all tools
    tools = [
        get_stock_price,
        get_financial_statements,
        get_technical_indicators,
        get_news_sentiment,
        get_analyst_recommendations
    ]

    # Define sub-agents
    subagents = [
        fundamental_analyst,
        technical_analyst,
        risk_analyst
    ]

    # Create the DeepAgent
    logger.info("Creating DeepAgent with 5 tools and 3 sub-agents")
    agent = create_deep_agent(
        tools=tools,
        instructions=RESEARCH_INSTRUCTIONS,
        subagents=subagents,
        model=ollama_model
    )

    logger.info("DeepAgent created successfully")
    return agent


def run_stock_research(query: str) -> str:
    """
    Run the stock research agent and return the analysis.

    Args:
        query: User's research query

    Returns:
        Research analysis report
    """
    try:
        logger.info(f"Running research query: {query[:100]}...")

        # Get the agent (could be cached in production)
        agent = create_research_agent()

        # Invoke the agent
        result = agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })

        # Extract the response
        messages = result.get("messages", [])
        output_text = ""

        if not messages:
            logger.warning("No messages returned in result")
            output_text = "Error: No response messages received."
        elif isinstance(messages[-1], dict):
            output_text = messages[-1].get("content", "")
        elif hasattr(messages[-1], "content"):
            output_text = messages[-1].content
        else:
            logger.error("Unrecognized message format")
            output_text = "Error: Invalid response message format."

        # Add generated files if any
        file_output = ""
        if "files" in result:
            file_output += "\n\n=== Generated Research Files ===\n"
            for filename, content in result["files"].items():
                preview = content[:500] + "..." if len(content) > 500 else content
                file_output += f"\n**{filename}**\n{preview}\n"

        return output_text + file_output

    except Exception as e:
        logger.exception("Research failed with exception")
        return f"Error: {str(e)}"


def main():
    """Main entry point for the application."""
    logger.info("Starting DeepAgents Stock Research Assistant")

    # Create the Gradio interface
    demo = create_gradio_interface(run_stock_research)

    # Launch the app
    logger.info(f"Launching Gradio interface on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    demo.launch(
        server_name=settings.SERVER_HOST,
        server_port=settings.SERVER_PORT,
        show_error=True
    )


if __name__ == "__main__":
    main()
