# 📊 DeepAgent Stock Research Assistant

> **A sophisticated AI-powered stock research agent built with LangChain DeepAgents that provides comprehensive financial analysis comparable to professional analysts.**

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)](https://langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Gradio](https://img.shields.io/badge/interface-gradio-orange.svg)](https://gradio.app/)

## 🚀 Overview

This project demonstrates how to build advanced AI research capabilities using LangChain's DeepAgent framework. Unlike simple chatbots, this system employs specialized sub-agents, systematic planning, and comprehensive tool integration to deliver professional-grade stock analysis.

<!-- Add hero screenshot here -->
[▶️ Watch the Demo](./deepagents.mp4)

![Screenshots](./screenshot.jpg)

### ✨ Key Features

- **🎯 Multi-Perspective Analysis**: Combines fundamental, technical, and risk analysis
- **🤖 Specialized Sub-Agents**: Expert analysts for different aspects of research
- **📊 Real-Time Data**: Live stock prices, financial statements, and technical indicators
- **🔄 Systematic Workflow**: Structured research methodology
- **🖥️ Web Interface**: User-friendly Gradio interface
- **📈 Professional Reports**: Investment recommendations with price targets
- **⚡ Fast Analysis**: Reduces research time from hours to minutes

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (Gradio)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Master DeepAgent Orchestrator                 │
├─────────────────────────────────────────────────────────────┤
│  Planning Tool | Virtual File System | System Prompt       │
└─────────────┬───────────────────────────────────┬─────────┘
              │                                   │
    ┌─────────▼──────────┐                ┌──────▼──────────┐
    │   Sub-Agents       │                │  Financial Tools │
    │                    │                │                  │
    │ • Fundamental      │                │ • Stock Price    │
    │ • Technical        │                │ • Financials     │
    │ • Risk Analysis    │                │ • Technical      │
    └────────────────────┘                │   Indicators     │
                                          └──────┬──────────┘
                                                 │
                                     ┌──────────▼──────────┐
                                     │   Data Sources      │
                                     │                     │
                                     │ • Yahoo Finance     │
                                     │ • Real-time APIs    │
                                     │ • Market Data       │
                                     └─────────────────────┘
```



## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Ollama (for local LLM hosting)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/deepagent-stock-research.git
   cd deepagent-stock-research
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull a model
   ollama pull gpt-oss
   ```

4. **Run the application**
   ```bash
   python research_agent.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:7860`

## 📦 Dependencies

The `requirements.txt` file includes:

```txt
# Core dependencies
deepagents
langchain-ollama
langchain-core
yfinance
gradio
pandas
numpy

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
```

## 🆕 What's New in v1.0.0

### Enhanced Features
- ✅ **News Sentiment Analysis** - Get recent news with automated sentiment scoring
- ✅ **Analyst Recommendations** - Access Wall Street analyst ratings and price targets
- ✅ **Export Functionality** - Save reports as JSON or Text files
- ✅ **Rate Limiting** - Prevents abuse with 10-second cooldown per user
- ✅ **Input Validation** - Comprehensive validation for all inputs
- ✅ **Intelligent Caching** - 1-hour cache for prices, 24-hour for financials
- ✅ **Retry Logic** - Exponential backoff for failed API calls (up to 3 attempts)
- ✅ **Enhanced UI** - Improved interface with status indicators

### Modular Architecture
The project has been refactored into a clean, maintainable structure:

```
deepagents/
├── src/
│   ├── agents/          # Specialized sub-agents
│   ├── tools/           # Financial data tools
│   ├── ui/              # Gradio interface
│   ├── utils/           # Utilities (config, cache, validation)
│   └── main.py          # Main entry point
├── tests/               # Unit tests
├── exports/             # Exported reports
└── research_agent.py    # Original (backward compatible)
```

### Running the New Version

```bash
# Method 1: Run as module (recommended)
python -m src.main

# Method 2: Install and use command
pip install -e .
deepagents-research

# Method 3: Backward compatible
python research_agent.py
```

## 🎯 Usage

### Basic Analysis

```python
# Example query
query = """
Conduct a comprehensive analysis of Apple Inc. (AAPL) for a 6-month investment horizon.
Include:
1. Current financial performance
2. Technical analysis with trading signals
3. Risk assessment
4. Investment recommendation with price targets
"""
```

### Advanced Queries

- **Portfolio Analysis**: "Compare AAPL, MSFT, and GOOGL for portfolio allocation"
- **Sector Research**: "Analyze the technology sector outlook for Q1 2025"
- **Risk Assessment**: "Evaluate the risks of investing in Tesla (TSLA)"
- **Technical Analysis**: "Provide technical analysis and entry points for NVDA"


## 🔧 Configuration

### Environment Variables

Configure the application via environment variables or `.env` file:

```bash
# LLM Configuration
OLLAMA_MODEL=gpt-oss           # Ollama model to use
TEMPERATURE=0.0                # LLM temperature (0-1)

# Server Configuration
SERVER_HOST=127.0.0.1          # Server host (use 0.0.0.0 for external access)
SERVER_PORT=7860               # Server port

# Cache Configuration
CACHE_TTL=3600                 # Cache time-to-live in seconds (1 hour)
CACHE_MAX_SIZE=100             # Maximum cache entries

# Rate Limiting
RATE_LIMIT_SECONDS=10          # Seconds between requests per user

# API Configuration
MAX_RETRIES=3                  # Max retry attempts for failed API calls
RETRY_MIN_WAIT=2               # Minimum wait between retries (seconds)
RETRY_MAX_WAIT=10              # Maximum wait between retries (seconds)

# Other
LOG_LEVEL=INFO                 # Logging level (DEBUG, INFO, WARNING, ERROR)
EXPORT_DIR=exports             # Directory for exported reports
```

### Model Configuration

```python
# Customize in src/utils/config.py or via environment variables
OLLAMA_MODEL="gpt-oss"         # Or "llama2", "codellama", etc.
TEMPERATURE=0.0                # For deterministic output
```

## 🛠️ Available Tools

The system includes 5 specialized financial tools:

### 1. get_stock_price
Get current stock price and basic company information.
- Current price, market cap, P/E ratio
- 52-week high/low
- Volume and average volume
- Dividend yield

### 2. get_financial_statements
Retrieve financial statements and calculated ratios.
- Revenue, net income, operating income
- Total assets, debt, equity, cash
- Calculated ratios: profit margin, ROA, ROE, debt-to-equity
- Operating and free cash flow

### 3. get_technical_indicators
Calculate technical indicators for chart analysis.
- Moving averages (SMA 20/50/200)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volume analysis
- Trend signals and trading recommendations

### 4. get_news_sentiment (NEW)
Analyze recent news articles with sentiment scoring.
- Recent news headlines and publishers
- Individual sentiment per article (positive/negative/neutral)
- Overall sentiment breakdown
- Publication dates and links

### 5. get_analyst_recommendations (NEW)
Access Wall Street analyst ratings and price targets.
- Analyst consensus rating (Strong Buy to Sell)
- Price targets (mean, high, low)
- Number of analyst opinions
- Recent recommendation changes
- Upside/downside potential calculation

### Adding Custom Tools

Create new tools in `src/tools/`:

```python
# src/tools/my_custom_tool.py
from langchain_core.tools import tool
from ..utils.validation import validate_stock_symbol

@tool
def my_custom_tool(symbol: str) -> str:
    """Your custom analysis logic here."""
    # Validate input
    symbol = normalize_stock_symbol(symbol)
    is_valid, error = validate_stock_symbol(symbol)
    if not is_valid:
        return json.dumps({"error": error})

    # Your implementation
    result = {"symbol": symbol, "data": "..."}
    return json.dumps(result, indent=2)
```

Then add to `src/tools/__init__.py` and `src/main.py`

### Customizing Sub-Agents

Create new sub-agents in `src/agents/`:

```python
# src/agents/esg.py
esg_analyst = {
    "name": "esg-analyst",
    "description": "Evaluates Environmental, Social, and Governance factors",
    "prompt": """You are an ESG specialist with expertise in evaluating
    corporate sustainability practices, social responsibility, and governance
    quality. Focus on material ESG factors that impact long-term value..."""
}
```

Then add to `src/agents/__init__.py` and `src/main.py`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/test_validation.py -v
```

## 📤 Exporting Reports

The new UI includes export functionality:

1. Complete your research analysis
2. Enter the stock symbol in the export section
3. Choose format (Text or JSON)
4. Click "Export Report"
5. Files are saved to `exports/` directory

**Export Formats:**
- **Text**: Human-readable format with headers
- **JSON**: Structured data for programmatic use

**Filename Format:** `{SYMBOL}_{TIMESTAMP}.{ext}`
Example: `AAPL_20251112_143052.txt`

## 📊 Example Output

```
=== STOCK RESEARCH REPORT ===

APPLE INC. (AAPL) INVESTMENT ANALYSIS
Generated: 2025-08-13 23:28:00

EXECUTIVE SUMMARY
Current Price: $184.12
Recommendation: BUY
Target Price: $210.00 (12-month)
Risk Level: MODERATE

FUNDAMENTAL ANALYSIS
• Revenue (TTM): $385.7B (+1.3% YoY)
• Net Income: $96.9B 
• P/E Ratio: 28.5x (Premium to sector avg: 24.1x)
• ROE: 147.4% (Excellent)
• Debt-to-Equity: 1.73 (Manageable)

TECHNICAL ANALYSIS
• Trend: BULLISH (Price > SMA20 > SMA50)
• RSI: 62.3 (Neutral-Bullish)
• Support Levels: $175, $165
• Resistance Levels: $195, $205

RISK ASSESSMENT
• Market Risk: MODERATE (Tech sector volatility)
• Company Risk: LOW (Strong balance sheet)
• Regulatory Risk: MODERATE (Antitrust concerns)

[Full detailed report continues...]
```


## 🚨 Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

## 🙏 Acknowledgments

- **LangChain Team** for the DeepAgent framework
- **Yahoo Finance** for providing free financial data APIs
- **Gradio Team** for the excellent UI framework
- **Ollama** for local LLM hosting capabilities


## 🌟 Star the Project

If you find this project useful, please consider giving it a star ⭐️ on GitHub!

---

**Built with ❤️ using LangChain DeepAgents**

*Transform your investment research with the power of specialized AI agents.*
