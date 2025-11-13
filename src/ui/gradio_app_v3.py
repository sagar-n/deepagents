"""Enhanced Gradio web interface v1.2.0 with bulletproof features.

New in v1.2.0:
- System Health monitoring dashboard
- Feedback and Analytics tab
- Confidence score display
- Multi-model provider status
- Memory system insights
"""

import time
import logging
import gradio as gr
from pathlib import Path
from typing import Optional, Generator, Callable
import json
from datetime import datetime

from ..utils.config import settings
from ..utils.validation import validate_query
from ..utils.database import get_database
from ..utils.analytics import get_tool_analytics
from ..utils.feedback import get_feedback_system
from ..utils.model_provider import get_model_provider

logger = logging.getLogger(__name__)

# Rate limiting storage
_rate_limit_tracker = {}


def rate_limit_check(user_id: str = "default") -> tuple[bool, Optional[str]]:
    """Check if user has exceeded rate limit."""
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
    """Export research report to JSON file."""
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
    """Export research report to text file."""
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


def create_gradio_interface_v2(
    research_function: Callable,
    research_function_streaming: Optional[Callable] = None,
    health_function: Optional[Callable] = None,
    feedback_function: Optional[Callable] = None
):
    """
    Create enhanced Gradio web interface v1.2.0 with bulletproof features.

    Args:
        research_function: The function to call for stock research
        research_function_streaming: Optional streaming version of research function
        health_function: Function to get system health status
        feedback_function: Function to submit user feedback

    Returns:
        Gradio Blocks interface
    """

    def run_research_with_validation_streaming(query: str, request: gr.Request) -> Generator[str, None, None]:
        """Run research with streaming output."""
        user_id = request.client.host if request else "default"

        # Validate query
        is_valid, error_msg = validate_query(query)
        if not is_valid:
            logger.warning(f"Invalid query from {user_id}: {error_msg}")
            yield f"❌ Error: {error_msg}"
            return

        # Check rate limit
        is_allowed, rate_error = rate_limit_check(user_id)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {user_id}")
            yield f"⏱️ {rate_error}"
            return

        # Run research with streaming
        logger.info(f"Starting streaming research for user {user_id}: {query[:50]}...")
        try:
            if research_function_streaming:
                for chunk in research_function_streaming(query):
                    yield chunk
            else:
                # Fallback to non-streaming with simulated progress
                yield "🔄 Processing...\n"
                result = research_function(query)
                # Handle dict or string return
                if isinstance(result, dict):
                    yield f"\n\n{result.get('report', str(result))}"
                else:
                    yield f"\n\n{result}"

        except Exception as e:
            logger.exception(f"Research failed for {user_id}")
            yield f"\n\n❌ Error: Failed to complete analysis: {str(e)}"

    def load_research_history() -> str:
        """Load research history for display."""
        try:
            db = get_database()
            history = db.get_recent_research(limit=20)

            if not history:
                return "No research history found."

            output = "# 📚 Research History\n\n"
            for item in history:
                metadata = item.get('metadata', {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}

                confidence = metadata.get('confidence_level', 'N/A')

                output += f"### {item['symbol']} - {item['created_at']}\n"
                output += f"**Query:** {item['query'][:100]}...\n"
                output += f"**ID:** {item['id']} | **Confidence:** {confidence}\n\n"
                output += "---\n\n"

            return output

        except Exception as e:
            logger.exception("Failed to load history")
            return f"Error loading history: {str(e)}"

    def load_specific_research(research_id: int) -> str:
        """Load specific research by ID."""
        try:
            if not research_id:
                return "Please enter a research ID"

            db = get_database()
            research = db.get_research_by_id(research_id)

            if not research:
                return f"Research ID {research_id} not found"

            output = f"# Research Report: {research['symbol']}\n\n"
            output += f"**Created:** {research['created_at']}\n"
            output += f"**Query:** {research['query']}\n\n"
            output += "=" * 80 + "\n\n"
            output += research['report']

            return output

        except Exception as e:
            logger.exception("Failed to load research")
            return f"Error: {str(e)}"

    def search_history(search_term: str) -> str:
        """Search research history."""
        try:
            if not search_term:
                return "Please enter a search term"

            db = get_database()
            results = db.search_research(search_term, limit=10)

            if not results:
                return f"No results found for '{search_term}'"

            output = f"# 🔍 Search Results for '{search_term}'\n\n"
            for item in results:
                output += f"### {item['symbol']} - {item['created_at']}\n"
                output += f"**Query:** {item['query'][:100]}...\n"
                output += f"**ID:** {item['id']}\n\n"
                output += "---\n\n"

            return output

        except Exception as e:
            logger.exception("Search failed")
            return f"Error: {str(e)}"

    def export_report(report: str, symbol: str, format: str) -> str:
        """Export report to file."""
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

    def get_system_health_display() -> str:
        """Get system health status for display."""
        try:
            if not health_function:
                return "Health monitoring not available"

            health = health_function()

            output = "# 🏥 System Health Dashboard\n\n"
            output += f"**Overall Status:** {health['overall_status'].upper()}\n"
            output += f"**Timestamp:** {datetime.fromtimestamp(health['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            output += f"**Uptime:** {health.get('uptime_seconds', 0):.1f}s\n\n"

            output += "## 🔧 Component Status\n\n"
            for component, status in health.get('components', {}).items():
                icon = "✅" if status.get('status') == 'healthy' else "⚠️" if status.get('status') == 'degraded' else "❌"
                output += f"{icon} **{component.replace('_', ' ').title()}**: {status.get('status', 'unknown')}\n"

                if 'details' in status:
                    for key, value in status['details'].items():
                        output += f"   - {key}: {value}\n"
                output += "\n"

            if 'issues' in health and health['issues']:
                output += "## ⚠️ Issues\n\n"
                for issue in health['issues']:
                    output += f"- {issue}\n"

            return output

        except Exception as e:
            logger.exception("Failed to get health status")
            return f"Error: {str(e)}"

    def get_analytics_display() -> str:
        """Get tool analytics for display."""
        try:
            analytics = get_tool_analytics()
            tool_stats = analytics.get_all_metrics()

            if not tool_stats:
                return "No analytics data available yet"

            output = "# 📊 Tool Analytics Dashboard\n\n"

            # Calculate rankings
            rankings = analytics.get_tool_rankings()

            output += "## 🏆 Top Performing Tools\n\n"
            for i, (tool_name, score) in enumerate(rankings[:5], 1):
                stats = tool_stats.get(tool_name, {})
                success_rate = stats.get('success_rate', 0) * 100
                avg_latency = stats.get('average_latency', 0)
                total_calls = stats.get('total_calls', 0)

                output += f"**{i}. {tool_name}** (Score: {score:.1f}/10)\n"
                output += f"   - Success Rate: {success_rate:.1f}%\n"
                output += f"   - Avg Latency: {avg_latency:.2f}s\n"
                output += f"   - Total Calls: {total_calls}\n\n"

            output += "## 📈 All Tools Summary\n\n"
            output += "| Tool | Calls | Success | Avg Latency | Score |\n"
            output += "|------|-------|---------|-------------|-------|\n"

            for tool_name, stats in tool_stats.items():
                success_rate = stats.get('success_rate', 0) * 100
                avg_latency = stats.get('average_latency', 0)
                total_calls = stats.get('total_calls', 0)
                score = rankings.get(tool_name, 0)

                output += f"| {tool_name} | {total_calls} | {success_rate:.0f}% | {avg_latency:.2f}s | {score:.1f} |\n"

            return output

        except Exception as e:
            logger.exception("Failed to get analytics")
            return f"Error: {str(e)}"

    def get_feedback_summary() -> str:
        """Get feedback summary for display."""
        try:
            feedback_system = get_feedback_system()
            summary = feedback_system.get_feedback_summary()

            if summary['total_feedback'] == 0:
                return "No feedback data available yet.\n\nPlease submit feedback on your research reports!"

            output = "# 📝 Feedback Summary\n\n"
            output += f"**Total Feedback:** {summary['total_feedback']}\n"
            output += f"**Average Rating:** {summary['avg_rating']:.1f}/5.0 ⭐\n\n"

            output += "## 📊 Rating Distribution\n\n"
            for rating, count in sorted(summary['rating_distribution'].items(), reverse=True):
                stars = "⭐" * rating
                bar = "█" * (count * 2)
                output += f"{stars} ({rating}): {bar} {count}\n"

            output += "\n## ✅ Most Helpful Aspects\n\n"
            for aspect, count in summary['top_helpful_aspects'][:10]:
                output += f"- {aspect}: {count} mentions\n"

            output += "\n## 📋 Most Requested Improvements\n\n"
            for aspect, count in summary['top_missing_aspects'][:10]:
                output += f"- {aspect}: {count} mentions\n"

            return output

        except Exception as e:
            logger.exception("Failed to get feedback summary")
            return f"Error: {str(e)}"

    def submit_user_feedback(research_id: int, rating: int, helpful: str, missing: str) -> str:
        """Submit user feedback."""
        try:
            if not research_id:
                return "❌ Please enter a research ID"

            if not rating or rating < 1 or rating > 5:
                return "❌ Please select a rating (1-5 stars)"

            # Parse comma-separated aspects
            helpful_list = [h.strip() for h in helpful.split(",")] if helpful else []
            missing_list = [m.strip() for m in missing.split(",")] if missing else []

            if feedback_function:
                success = feedback_function(research_id, rating, helpful_list, missing_list)
                if success:
                    return f"✅ Thank you for your feedback! (Research ID: {research_id})"
                else:
                    return "❌ Failed to submit feedback"
            else:
                return "❌ Feedback system not available"

        except Exception as e:
            logger.exception("Failed to submit feedback")
            return f"❌ Error: {str(e)}"

    # Create interface
    with gr.Blocks(title="DeepAgents Stock Research v1.2.0", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📊 DeepAgents Stock Research Assistant v1.2.0 "Bulletproof"

            ### 🚀 NEW in v1.2.0:
            - **Multi-Model Fallback** - Automatic Ollama → Groq → OpenAI → Claude failover
            - **A-Mem Dual-Layer Memory** - Learns your preferences over time
            - **Self-Healing** - Circuit breakers protect against failures
            - **Health Monitoring** - Real-time system status dashboard
            - **Reflection Agent** - Quality gate before delivery
            - **Confidence Scores** - Know how reliable each analysis is
            - **Feedback & Analytics** - Continuous improvement through user input

            Get comprehensive stock analysis powered by specialized AI agents combining
            **fundamental**, **technical**, **risk**, and **comparison** analysis with **bulletproof reliability**.
            """
        )

        with gr.Tabs():
            # Tab 1: Main Analysis
            with gr.Tab("🔍 Stock Analysis"):
                gr.Markdown(
                    """
                    ### Example Queries:
                    - *"Comprehensive analysis of Apple (AAPL) for 6-month horizon"*
                    - *"Compare AAPL, MSFT, and GOOGL for portfolio allocation"*
                    - *"Technical analysis and entry points for NVDA"*
                    - *"Risk assessment for Tesla (TSLA)"*
                    """
                )

                with gr.Row():
                    with gr.Column(scale=2):
                        query_input = gr.Textbox(
                            label="Research Query",
                            lines=6,
                            placeholder="Enter your stock research request...\n\nFor comparison: 'Compare AAPL and MSFT'",
                            info="Supports single stock or multi-stock comparison queries"
                        )

                        with gr.Row():
                            run_button = gr.Button("🚀 Run Analysis (Streaming)", variant="primary", size="lg")
                            clear_button = gr.Button("🗑️ Clear", size="lg")

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
                    label="Research Report (Streaming with Confidence)",
                    lines=30,
                    max_lines=50,
                    show_copy_button=True,
                    interactive=False
                )

            # Tab 2: Research History
            with gr.Tab("📚 Research History"):
                gr.Markdown("### Browse your research history and reload past analyses")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Recent Research")
                        refresh_button = gr.Button("🔄 Refresh History")
                        history_display = gr.Textbox(
                            label="Recent Analyses",
                            lines=20,
                            interactive=False
                        )

                    with gr.Column():
                        gr.Markdown("#### Load Specific Report")
                        research_id_input = gr.Number(
                            label="Research ID",
                            precision=0,
                            info="Enter ID from history list"
                        )
                        load_button = gr.Button("📄 Load Report")

                        gr.Markdown("#### Search History")
                        search_input = gr.Textbox(
                            label="Search Term",
                            placeholder="Enter stock symbol or keyword..."
                        )
                        search_button = gr.Button("🔍 Search")

                report_display = gr.Textbox(
                    label="Loaded Report",
                    lines=25,
                    interactive=False,
                    show_copy_button=True
                )

            # Tab 3: System Health (NEW v1.2.0)
            with gr.Tab("🏥 System Health"):
                gr.Markdown("### Monitor system health and component status")

                health_refresh_button = gr.Button("🔄 Refresh Health Status", size="lg")

                health_display = gr.Textbox(
                    label="System Health Dashboard",
                    lines=30,
                    interactive=False
                )

                gr.Markdown(
                    """
                    #### Health Status Legend:
                    - ✅ **Healthy** - Component operating normally
                    - ⚠️ **Degraded** - Component experiencing issues but functional
                    - ❌ **Unhealthy** - Component failure detected
                    """
                )

            # Tab 4: Feedback & Analytics (NEW v1.2.0)
            with gr.Tab("📊 Feedback & Analytics"):
                gr.Markdown("### Submit feedback and view analytics")

                with gr.Tabs():
                    with gr.Tab("📝 Submit Feedback"):
                        gr.Markdown("Help us improve by rating your research experience!")

                        feedback_research_id = gr.Number(
                            label="Research ID",
                            precision=0,
                            info="Get this from the history tab"
                        )

                        feedback_rating = gr.Radio(
                            label="Rating",
                            choices=[5, 4, 3, 2, 1],
                            value=5,
                            info="5 stars = Excellent, 1 star = Poor"
                        )

                        feedback_helpful = gr.Textbox(
                            label="What was helpful?",
                            placeholder="Enter comma-separated aspects (e.g., 'clear recommendation, comprehensive data, good risk analysis')",
                            lines=3
                        )

                        feedback_missing = gr.Textbox(
                            label="What was missing?",
                            placeholder="Enter comma-separated aspects (e.g., 'more charts, sector comparison, historical context')",
                            lines=3
                        )

                        submit_feedback_button = gr.Button("📨 Submit Feedback", variant="primary", size="lg")

                        feedback_status = gr.Textbox(
                            label="Submission Status",
                            interactive=False
                        )

                    with gr.Tab("📊 Tool Analytics"):
                        analytics_refresh_button = gr.Button("🔄 Refresh Analytics")

                        analytics_display = gr.Textbox(
                            label="Tool Performance Analytics",
                            lines=25,
                            interactive=False
                        )

                    with gr.Tab("📝 Feedback Summary"):
                        feedback_refresh_button = gr.Button("🔄 Refresh Feedback Summary")

                        feedback_summary_display = gr.Textbox(
                            label="User Feedback Summary",
                            lines=25,
                            interactive=False
                        )

        gr.Markdown(
            """
            ---
            ### ℹ️ Information

            **🆕 v1.2.0 "Bulletproof" Updates:**
            - Multi-model provider with automatic fallback chain
            - A-Mem adaptive memory learns your preferences
            - Self-healing circuit breakers prevent cascading failures
            - Real-time health monitoring and diagnostics
            - Reflection agent ensures quality before delivery
            - Confidence scoring on all recommendations
            - User feedback system for continuous improvement
            - Tool analytics track performance metrics

            **Previous Features:**
            - Real-time streaming responses
            - Automatic research history saving
            - Multi-stock comparison agent
            - 3-5x faster parallel data fetching

            **Rate Limit:** One request per 10 seconds per user
            **Powered by:** LangChain DeepAgents Framework + Multi-Model AI
            **Data Source:** Yahoo Finance (Real-time)

            ⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice.
            """
        )

        # Event handlers - Analysis Tab
        run_button.click(
            fn=run_research_with_validation_streaming,
            inputs=query_input,
            outputs=output_box
        )

        clear_button.click(
            fn=lambda: ("", ""),
            inputs=None,
            outputs=[query_input, output_box]
        )

        export_button.click(
            fn=export_report,
            inputs=[output_box, symbol_input, export_format],
            outputs=export_status
        )

        # Event handlers - History Tab
        refresh_button.click(
            fn=load_research_history,
            inputs=None,
            outputs=history_display
        )

        load_button.click(
            fn=load_specific_research,
            inputs=research_id_input,
            outputs=report_display
        )

        search_button.click(
            fn=search_history,
            inputs=search_input,
            outputs=report_display
        )

        # Event handlers - Health Tab
        health_refresh_button.click(
            fn=get_system_health_display,
            inputs=None,
            outputs=health_display
        )

        # Event handlers - Feedback & Analytics Tab
        submit_feedback_button.click(
            fn=submit_user_feedback,
            inputs=[feedback_research_id, feedback_rating, feedback_helpful, feedback_missing],
            outputs=feedback_status
        )

        analytics_refresh_button.click(
            fn=get_analytics_display,
            inputs=None,
            outputs=analytics_display
        )

        feedback_refresh_button.click(
            fn=get_feedback_summary,
            inputs=None,
            outputs=feedback_summary_display
        )

        # Load initial data on page load
        demo.load(
            fn=load_research_history,
            inputs=None,
            outputs=history_display
        )

        demo.load(
            fn=get_system_health_display,
            inputs=None,
            outputs=health_display
        )

    return demo
