## Upgrade Guide: v0.1.0 → v1.0.0

This guide helps you upgrade from the original single-file version to the new modular v1.0.0.

### What's Changed

The project has been refactored from a single `research_agent.py` file into a modular package structure with enhanced features.

### Quick Start

#### Option 1: Use New Modular Version (Recommended)

```bash
# Install/update dependencies
pip install -r requirements.txt

# Run the new modular version
python -m src.main

# Or install as package and use command
pip install -e .
deepagents-research
```

#### Option 2: Backward Compatible

```bash
# The old research_agent.py still works but uses new code underneath
python research_agent_v2.py
```

### New Directory Structure

```
deepagents/
├── src/                      # NEW: Modular source code
│   ├── agents/              # Sub-agent configurations
│   ├── tools/               # Financial data tools
│   ├── ui/                  # Gradio interface
│   ├── utils/               # Utilities (cache, validation, config)
│   └── main.py              # Main entry point
├── tests/                    # NEW: Unit tests
├── exports/                  # NEW: Exported reports location
├── research_agent.py         # Original file (preserved)
├── research_agent_v2.py      # NEW: Backward-compatible wrapper
├── requirements.txt          # Updated with test dependencies
├── setup.py                  # NEW: Package installation
├── .gitignore               # NEW: Ignore Python artifacts
├── LICENSE                   # NEW: MIT License
└── readme.md                 # Updated documentation
```

### New Features You Get

1. **Better Performance**
   - API call caching (1 hour for prices, 24 hours for financials)
   - Retry logic with exponential backoff
   - Input validation to prevent unnecessary API calls

2. **More Data**
   - News sentiment analysis
   - Analyst recommendations and price targets
   - Enhanced technical indicators (MACD, volume analysis)
   - More fundamental metrics (profit margins, ROA, ROE)

3. **Better UX**
   - Rate limiting (prevents abuse)
   - Export to JSON/Text
   - Better error messages
   - Status indicators

4. **Production Ready**
   - Comprehensive error handling
   - Unit tests
   - Configuration via environment variables
   - Modular, maintainable code

### Configuration

You can now configure the app via environment variables:

```bash
# Create a .env file (optional)
OLLAMA_MODEL=gpt-oss
TEMPERATURE=0.0
SERVER_HOST=127.0.0.1
SERVER_PORT=7860
CACHE_TTL=3600
RATE_LIMIT_SECONDS=10
LOG_LEVEL=INFO
```

### Breaking Changes

**None!** The original `research_agent.py` is preserved for backward compatibility.

### Migration Path

If you made customizations to the original `research_agent.py`:

1. **Custom Tools**: Move to `src/tools/` directory
2. **Custom Agents**: Update `src/agents/` configurations
3. **UI Changes**: Modify `src/ui/gradio_app.py`
4. **Configuration**: Add to `src/utils/config.py`

### Testing

Run the test suite to verify everything works:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Rollback

If you need to rollback to the original version:

```bash
# The original research_agent.py is unchanged
python research_agent.py
```

### Getting Help

- Issues: https://github.com/MindXpansion/deepagents/issues
- Documentation: See updated README.md

### Next Steps

1. Try the new features (news sentiment, analyst recommendations)
2. Configure via environment variables for your setup
3. Use export functionality to save reports
4. Run the test suite to ensure everything works
5. Consider contributing improvements back to the project!
