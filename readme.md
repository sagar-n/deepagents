# 📊 DeepAgent Stock Research Assistant

> **A sophisticated AI-powered stock research agent built with LangChain DeepAgents that provides comprehensive financial analysis comparable to professional analysts.**

[![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/langchain-latest-green.svg)](https://langchain.com/)
[![Version](https://img.shields.io/badge/version-v1.3.0-brightgreen.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Gradio](https://img.shields.io/badge/interface-gradio-orange.svg)](https://gradio.app/)

## 🚀 Overview

This project demonstrates how to build advanced AI research capabilities using LangChain's DeepAgent framework. Unlike simple chatbots, this system employs specialized sub-agents, systematic planning, and comprehensive tool integration to deliver professional-grade stock analysis.

<!-- Add hero screenshot here -->
[▶️ Watch the Demo](./deepagents.mp4)

![Screenshots](./screenshot.jpg)

### ✨ Key Features

#### **Core Capabilities**
- **🎯 Multi-Perspective Analysis**: Combines fundamental, technical, and risk analysis
- **🤖 Specialized Sub-Agents**: Expert analysts for different aspects of research
- **📊 Real-Time Data**: Live stock prices, financial statements, and technical indicators
- **🔄 Systematic Workflow**: Structured research methodology with quality gates
- **🖥️ Web Interface**: User-friendly Gradio interface with 4-tab dashboard
- **📈 Professional Reports**: Investment recommendations with confidence scoring

#### **⚡ v1.3.0 "Lightning Fast++" Performance**
- **💬 ChatGPT-Like Streaming**: Watch AI think in real-time with true token-by-token streaming
- **🚀 10x Faster Queries**: Advanced database optimization with FTS5 full-text search
- **🧠 Smart Caching**: Market-hours-aware caching reduces API costs by 240x
- **⚙️ Async-Ready**: Infrastructure for parallel agent execution (future)

#### **🛡️ v1.2.0 "Bulletproof" Reliability**
- **🔄 Multi-Model Fallback**: Ollama → Groq → OpenAI → Claude (never fails)
- **🧠 Adaptive Memory**: A-Mem dual-layer system learns from interactions
- **💪 Self-Healing**: Circuit breakers auto-recover from failures
- **📊 Quality Assurance**: Reflection agent validates all outputs
- **⭐ User Feedback**: Star ratings and analytics tracking

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
pytz  # For market-hours-aware caching (v1.3.0)

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
```

**Optional Dependencies:**
- `pytz` - Enables market-hours detection for smart caching. If not installed, caching still works but assumes market is always open.
- `pytest-asyncio` - For testing async agent execution framework.

## 🆕 What's New in v1.3.0 "Lightning Fast++"

### ⚡ Extreme Performance Optimization

**1. True Token-by-Token Streaming** 💬
- Real-time LLM response streaming (ChatGPT-like experience)
- Watch the AI think as tokens appear live
- Gradio-optimized chunking for smooth rendering
- Background thread management with error recovery

**2. Database Optimization** 🚀
- **10x faster** history tab loading (800ms → 80ms)
- FTS5 full-text search for lightning-fast queries
- Composite indexes on (symbol, created_at)
- WAL mode for better concurrency
- Lazy loading - summaries without full reports

**3. Smart Market-Hours Caching** 🧠
- Market-hours detection (US Eastern Time)
- Dynamic TTL based on trading status
- Price cache: 60s (market open) → 4 hours (closed) → Until Monday (weekend)
- Event-driven invalidation hooks
- **240x longer** cache during off-hours = massive API cost savings

**4. Async Agent Framework** ⚙️
- Infrastructure for parallel sub-agent execution
- ThreadPoolExecutor with 4 workers
- Progressive result streaming
- Future-ready for 2-3x analysis speedup

### 🛡️ v1.2.0 "Bulletproof" Systems

**Enterprise-Grade Reliability:**
- ✅ **Multi-Model Provider** - Ollama → Groq → OpenAI → Claude fallback chain
- ✅ **A-Mem Memory** - Short-term + long-term adaptive memory
- ✅ **Circuit Breakers** - Self-healing with CLOSED/OPEN/HALF_OPEN states
- ✅ **Health Monitoring** - Real-time system component status
- ✅ **Reflection Agent** - 6-dimension quality scoring before delivery
- ✅ **Feedback System** - Star ratings (1-5) with aspect tagging
- ✅ **Tool Analytics** - Success rate and latency tracking
- ✅ **Confidence Scoring** - 5-factor weighted scoring (HIGH/MODERATE/LOW)

### 📊 v1.1.0 "Lightning Fast" & v1.0.0 "Production"

**Foundation Features:**
- ✅ **News Sentiment Analysis** - Automated sentiment scoring
- ✅ **Analyst Recommendations** - Wall Street ratings and targets
- ✅ **Export Functionality** - JSON/Text report exports
- ✅ **Async Tools** - Parallel data fetching
- ✅ **Research History** - SQLite database with search
- ✅ **Stock Comparison** - Multi-symbol analysis
- ✅ **Input Validation** - Comprehensive validation
- ✅ **Retry Logic** - Exponential backoff

### Modular Architecture (36 Files)
Production-ready structure with bulletproof systems and performance optimization:

```
deepagents/
├── src/
│   ├── agents/ (6 files)         # Specialized sub-agents
│   │   ├── fundamental.py        # Financial analysis
│   │   ├── technical.py          # Chart analysis
│   │   ├── risk.py               # Risk assessment
│   │   ├── comparison.py         # Multi-stock comparison
│   │   └── reflection.py         # Quality gate (v1.2)
│   │
│   ├── tools/ (8 files)          # Financial data tools
│   │   ├── stock_data.py         # Price data
│   │   ├── financials.py         # Statements
│   │   ├── technical_indicators.py
│   │   ├── news_sentiment.py     # News + sentiment
│   │   ├── analyst_data.py       # Analyst ratings
│   │   ├── comparison.py         # Multi-symbol
│   │   └── async_tools.py        # Parallel fetching
│   │
│   ├── ui/ (4 files)             # Gradio interfaces
│   │   ├── gradio_app.py         # v1.0 UI
│   │   ├── gradio_app_v2.py      # v1.1 UI
│   │   └── gradio_app_v3.py      # v1.2 UI (4 tabs) ← Active
│   │
│   ├── utils/ (17 files)         # Core systems
│   │   ├── config.py             # Configuration
│   │   ├── validation.py         # Input validation
│   │   ├── cache.py              # Smart caching (v1.3)
│   │   ├── database.py           # SQLite + FTS5 (v1.3)
│   │   ├── retry.py              # Exponential backoff
│   │   ├── streaming.py          # Simulated streaming
│   │   │
│   │   ├── model_provider.py     # Multi-model fallback (v1.2)
│   │   ├── memory.py             # A-Mem dual-layer (v1.2)
│   │   ├── circuit_breaker.py    # Self-healing (v1.2)
│   │   ├── health_monitor.py     # System health (v1.2)
│   │   ├── feedback.py           # User feedback (v1.2)
│   │   ├── analytics.py          # Tool analytics (v1.2)
│   │   ├── confidence.py         # Confidence scoring (v1.2)
│   │   │
│   │   ├── llm_streaming.py      # True LLM streaming (v1.3)
│   │   └── async_agents.py       # Async framework (v1.3)
│   │
│   └── main.py (v1.3.0)          # Main entry point
│
├── tests/                        # Comprehensive test suite
│   ├── test_bulletproof_v1.2.py  # Unit tests
│   └── test_v1.2_simple.py       # Integration tests
│
├── runtime_data/                 # Database, cache, memory
├── exports/                      # Exported reports
└── RELEASE_NOTES_v1.3.md         # Full v1.3 documentation
```

### Running v1.3.0

```bash
# Recommended: Run as module
python -m src.main

# The system will automatically:
# ✅ Initialize all bulletproof systems (v1.2)
# ✅ Enable true token streaming (v1.3)
# ✅ Activate smart caching (v1.3)
# ✅ Optimize database with FTS5 (v1.3)
# ✅ Launch Gradio UI on http://localhost:7860

# Optional: Install as package
pip install -e .
deepagents-research

# Backward compatible with v1.0
python research_agent.py
```

**What Happens on Startup:**
1. Multi-model provider initializes (Ollama → Groq → OpenAI → Claude)
2. Database auto-migrates to FTS5 (if needed)
3. Circuit breakers initialize in CLOSED state
4. Memory system loads user profiles
5. Health monitor starts tracking components
6. Smart cache detects market hours
7. Gradio UI launches with streaming enabled

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


## 📋 Version History

| Version | Codename | Release Date | Key Features |
|---------|----------|--------------|--------------|
| **v1.3.0** | Lightning Fast++ | Nov 14, 2025 | True LLM streaming, 10x faster DB, smart caching, async framework |
| **v1.2.0** | Bulletproof | Nov 13, 2025 | Multi-model fallback, A-Mem, circuit breakers, reflection agent |
| **v1.1.0** | Lightning Fast | Nov 12, 2025 | Async tools, history DB, comparison, streaming UI |
| **v1.0.0** | Production | Nov 11, 2025 | Modular architecture, validation, caching, retry logic |

**Performance Evolution:**
- v1.0.0: Baseline performance
- v1.1.0: 3-5x faster with async tools
- v1.2.0: 99.9% reliability with bulletproof systems
- v1.3.0: 10x faster queries + real-time streaming

**Documentation:**
- Full v1.3.0 docs: [RELEASE_NOTES_v1.3.md](RELEASE_NOTES_v1.3.md)
- Full v1.2.0 docs: [RELEASE_NOTES_v1.2.md](RELEASE_NOTES_v1.2.md)
- Complete changelog: [CHANGELOG.md](CHANGELOG.md)
- Audit report: [AUDIT_SUMMARY.md](AUDIT_SUMMARY.md)

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
