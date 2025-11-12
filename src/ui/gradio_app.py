"""Gradio web interface with rate limiting and export functionality."""

import time
import logging
import gradio as gr
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from ..utils.config import settings
from ..utils.validation import validate_query

logger = logging.getLogger(__name__)

# Rate limiting storage
_rate_limit_tracker = {}


def rate_limit_check(user_id: str = "default") -> tuple[bool, Optional[str]]:
    """
    Check if user has exceeded rate limit.

    Args:
        user_id: User identifier (IP or session ID)

    Returns:
        Tuple of (is_allowed, error_message)
    """
    current_time = time.time()

    if user_id in _rate_limit_tracker:
        last_request_time = _rate_limit_tracker[user_id]
        time_since_last = current_time - last_request_time

        if time_since_last < settings.RATE_LIMIT_SECONDS:
            wait_time = settings.RATE_LIMIT_SECONDS - time_since_last
            return False, f"Please wait {wait_time:.1f} seconds before submitting another request."

    _rate_limit_tracker[user_id] = current_time
    return True, None


def export_to_json(report: str, symbol: str) -> str:
    """
    Export research report to JSON file.

    Args:
        report: Research report text
        symbol: Stock symbol

    Returns:
        Path to exported file
    """
    export_dir = Path(settings.EXPORT_DIR)
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{timestamp}.json"
    filepath = export_dir / filename

    data = {
        "symbol": symbol,
        "timestamp": timestamp,
        "report": report
    }

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    return str(filepath)


def export_to_text(report: str, symbol: str) -> str:
    """
    Export research report to text file.

    Args:
        report: Research report text
        symbol: Stock symbol

    Returns:
        Path to exported file
    """
    export_dir = Path(settings.EXPORT_DIR)
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{timestamp}.txt"
    filepath = export_dir / filename

    with open(filepath, 'w') as f:
        f.write(f"Stock Research Report: {symbol}\n")
        f.write(f"Generated: {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        f.write(report)

    return str(filepath)


def create_gradio_interface(research_function):
    """
    Create Gradio web interface for the stock research agent.

    Args:
        research_function: The function to call for stock research

    Returns:
        Gradio Blocks interface
    """

    def run_research_with_validation(query: str, request: gr.Request) -> tuple[str, str]:
        """
        Run research with validation and rate limiting.

        Args:
            query: Research query
            request: Gradio request object

        Returns:
            Tuple of (result, status_message)
        """
        # Get user identifier (IP address)
        user_id = request.client.host if request else "default"

        # Validate query
        is_valid, error_msg = validate_query(query)
        if not is_valid:
            logger.warning(f"Invalid query from {user_id}: {error_msg}")
            return "", f"❌ Error: {error_msg}"

        # Check rate limit
        is_allowed, rate_error = rate_limit_check(user_id)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {user_id}")
            return "", f"⏱️ {rate_error}"

        # Run research
        logger.info(f"Starting research for user {user_id}: {query[:50]}...")
        try:
            result = research_function(query)
            logger.info(f"Research completed for {user_id}")
            return result, "✅ Analysis completed successfully!"
        except Exception as e:
            logger.exception(f"Research failed for {user_id}")
            return "", f"❌ Error: Failed to complete analysis: {str(e)}"

    def export_report(report: str, symbol: str, format: str) -> str:
        """
        Export report to file.

        Args:
            report: Report content
            symbol: Stock symbol
            format: Export format (json or text)

        Returns:
            Export status message
        """
        if not report:
            return "❌ No report to export"

        if not symbol:
            symbol = "UNKNOWN"

        try:
            if format == "JSON":
                filepath = export_to_json(report, symbol)
            else:
                filepath = export_to_text(report, symbol)

            return f"✅ Report exported to: {filepath}"
        except Exception as e:
            logger.exception("Export failed")
            return f"❌ Export failed: {str(e)}"

    # Create interface
    with gr.Blocks(title="DeepAgents Stock Research", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📊 DeepAgents Stock Research Assistant

            Get comprehensive stock analysis powered by specialized AI agents.
            The system combines **fundamental**, **technical**, and **risk** analysis
            with real-time market data.

            ### Example Queries:
            - *"Comprehensive analysis of Apple Inc. (AAPL) for a 6-month investment horizon"*
            - *"Compare AAPL and MSFT for portfolio allocation"*
            - *"Technical analysis and entry points for NVDA"*
            - *"Risk assessment for investing in Tesla (TSLA)"*
            """
        )

        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="Research Query",
                    lines=6,
                    placeholder="Enter your stock research request here...\n\nExample: Analyze Apple Inc. (AAPL) including fundamental metrics, technical signals, and risk factors.",
                    info="Minimum 5 characters, maximum 2000 characters"
                )

                with gr.Row():
                    run_button = gr.Button("🔍 Run Analysis", variant="primary", size="lg")
                    clear_button = gr.Button("🗑️ Clear", size="lg")

                status_box = gr.Textbox(
                    label="Status",
                    interactive=False,
                    show_label=True
                )

            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Export Options")

                symbol_input = gr.Textbox(
                    label="Stock Symbol",
                    placeholder="AAPL",
                    info="For export filename"
                )

                export_format = gr.Radio(
                    label="Export Format",
                    choices=["Text", "JSON"],
                    value="Text"
                )

                export_button = gr.Button("💾 Export Report")

                export_status = gr.Textbox(
                    label="Export Status",
                    interactive=False
                )

        output_box = gr.Textbox(
            label="Research Report",
            lines=25,
            max_lines=50,
            show_copy_button=True,
            interactive=False
        )

        gr.Markdown(
            """
            ---
            ### ℹ️ Information

            **Rate Limit:** One request per 10 seconds per user
            **Powered by:** LangChain DeepAgents Framework
            **Data Source:** Yahoo Finance (Real-time)

            ⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice.
            """
        )

        # Event handlers
        run_button.click(
            fn=run_research_with_validation,
            inputs=query_input,
            outputs=[output_box, status_box]
        )

        clear_button.click(
            fn=lambda: ("", "", ""),
            inputs=None,
            outputs=[query_input, output_box, status_box]
        )

        export_button.click(
            fn=export_report,
            inputs=[output_box, symbol_input, export_format],
            outputs=export_status
        )

    return demo
