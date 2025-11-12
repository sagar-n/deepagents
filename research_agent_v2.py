"""
Backward-compatible entry point for DeepAgents Stock Research Assistant.

This file maintains compatibility with the original research_agent.py
while using the new modular architecture underneath.

Usage:
    python research_agent_v2.py

Note: For new deployments, use:
    python -m src.main
"""

import logging
import sys
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import from new modular structure
try:
    from src.main import main

    if __name__ == "__main__":
        logging.info("Starting DeepAgents via backward-compatible entry point")
        main()

except ImportError as e:
    # Fallback error message
    print(f"Error: Unable to import modular components: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    print("\nOr run the new modular version:")
    print("  python -m src.main")
    sys.exit(1)
