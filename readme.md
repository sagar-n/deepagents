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

Create a `requirements.txt` file with:

```txt
deepagents
langchain-ollama
langchain-core
yfinance
gradio
pandas
numpy
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

### Model Configuration

```python
# Customize the LLM model
ollama_model = ChatOllama(
    model="your-preferred-model",  # e.g., "llama2", "codellama"
    temperature=0,                 # Adjust for creativity vs consistency
)
```

### Adding Custom Tools

```python
@tool
def custom_analysis_tool(symbol: str) -> str:
    """Your custom analysis logic here."""
    # Implementation
    return results

# Add to tools list
tools = [
    get_stock_price,
    get_financial_statements,
    get_technical_indicators,
    custom_analysis_tool  # Your custom tool
]
```

### Customizing Sub-Agents

```python
# Add new specialized sub-agent
esg_analyst = {
    "name": "esg-analyst",
    "description": "Evaluates Environmental, Social, and Governance factors",
    "prompt": """You are an ESG specialist..."""
}

subagents = [fundamental_analyst, technical_analyst, risk_analyst, esg_analyst]
```

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
