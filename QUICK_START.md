# Quick Start Guide - DeepAgents v1.0.0

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start Ollama (if not running)
```bash
ollama pull gpt-oss
# Ollama should be running in the background
```

### Step 3: Launch the Application
```bash
# Method A: New modular version (recommended)
python -m src.main

# Method B: Backward compatible
python research_agent_v2.py

# Method C: Install and use command
pip install -e .
deepagents-research
```

Open your browser to **http://localhost:7860**

---

## 💡 Example Queries to Try

### Comprehensive Analysis
```
Conduct a comprehensive analysis of Apple Inc. (AAPL) for a 6-month
investment horizon. Include current financial performance, technical
analysis with trading signals, risk assessment, and investment
recommendation with price targets.
```

### Quick Technical Analysis
```
Provide technical analysis and entry points for NVIDIA (NVDA)
```

### News & Sentiment
```
What's the recent news sentiment for Tesla (TSLA)?
```

### Analyst Opinion
```
What are Wall Street analysts saying about Microsoft (MSFT)?
```

### Risk Assessment
```
Evaluate the risks of investing in Amazon (AMZN)
```

### Portfolio Comparison
```
Compare Apple (AAPL) and Microsoft (MSFT) for portfolio allocation
```

---

## 🎯 New Features You Should Try

1. **Export Reports**
   - Complete your analysis
   - Enter stock symbol in export section
   - Choose Text or JSON format
   - Click "Export Report"
   - Find file in `exports/` directory

2. **News Sentiment**
   - Get recent headlines with automated sentiment scoring
   - See positive/negative/neutral breakdown

3. **Analyst Recommendations**
   - Access Wall Street price targets
   - See consensus ratings (Buy/Hold/Sell)
   - View upside/downside potential

---

## ⚙️ Configuration (Optional)

Create a `.env` file in the project root:

```bash
# LLM Settings
OLLAMA_MODEL=gpt-oss
TEMPERATURE=0.0

# Server Settings
SERVER_HOST=127.0.0.1
SERVER_PORT=7860

# Performance Settings
CACHE_TTL=3600              # Cache for 1 hour
RATE_LIMIT_SECONDS=10       # 10 seconds between requests

# Debugging
LOG_LEVEL=INFO              # Use DEBUG for detailed logs
```

---

## 🧪 Run Tests (Optional)

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📊 Tool Overview

| Tool | Purpose | Example Use |
|------|---------|-------------|
| **get_stock_price** | Current price & basic info | "What's the current price of AAPL?" |
| **get_financial_statements** | Financial data & ratios | "Show me MSFT's financial health" |
| **get_technical_indicators** | Chart analysis & signals | "Technical analysis for GOOGL" |
| **get_news_sentiment** | Recent news with sentiment | "Latest news on TSLA" |
| **get_analyst_recommendations** | Wall Street ratings | "What do analysts think of NVDA?" |

---

## 🆘 Troubleshooting

### "Connection Error"
- Ensure Ollama is running: `ollama serve`
- Check if model is downloaded: `ollama list`

### "No data for symbol"
- Verify symbol is correct (e.g., "AAPL" not "Apple")
- Some symbols may not have complete data

### "Rate limit exceeded"
- Wait 10 seconds between requests
- This prevents API abuse

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

---

## 📖 More Information

- **Full Documentation:** See `readme.md`
- **What's New:** See `CHANGELOG.md`
- **Migration Guide:** See `UPGRADE_GUIDE.md`
- **Complete Summary:** See `IMPLEMENTATION_SUMMARY.md`

---

## 🎓 Next Steps

1. ✅ Try different query types
2. ✅ Export a report to see the format
3. ✅ Configure via environment variables
4. ✅ Check out the new news and analyst tools
5. ✅ Explore the modular code structure

**Enjoy your enhanced stock research assistant!** 🚀

---

*For issues or questions, refer to the documentation or create a GitHub issue.*
