"""Tool analytics and performance tracking system.

Tracks tool usage, performance, and value to optimize system behavior.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolAnalytics:
    """
    Analytics system for tracking tool performance and value.

    Metrics tracked:
    - Call count and frequency
    - Success/failure rates
    - Average latency
    - User value scores (from feedback)
    - Error patterns
    """

    def __init__(self, analytics_file: str = "tool_analytics.json"):
        """
        Initialize tool analytics.

        Args:
            analytics_file: Path to analytics storage file
        """
        self.analytics_file = Path(analytics_file)
        self.analytics = self._load_analytics()
        self.session_calls = defaultdict(lambda: {"calls": 0, "time": 0.0})

    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics from file."""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except:
                logger.warning("Failed to load analytics, starting fresh")

        return {}

    def _save_analytics(self):
        """Save analytics to file."""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save analytics: {e}")

    def _get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get or create tool statistics."""
        if tool_name not in self.analytics:
            self.analytics[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "total_latency": 0.0,
                "min_latency": float('inf'),
                "max_latency": 0.0,
                "errors": [],
                "value_scores": [],
                "last_called": None
            }
        return self.analytics[tool_name]

    def record_call(
        self,
        tool_name: str,
        success: bool,
        latency: float,
        error: Optional[str] = None
    ):
        """
        Record a tool call.

        Args:
            tool_name: Name of the tool
            success: Whether call succeeded
            latency: Call latency in seconds
            error: Error message if failed
        """
        stats = self._get_tool_stats(tool_name)

        stats["total_calls"] += 1
        stats["last_called"] = time.time()

        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
            if error:
                # Keep last 10 errors
                stats["errors"].append({
                    "error": error,
                    "timestamp": time.time()
                })
                if len(stats["errors"]) > 10:
                    stats["errors"] = stats["errors"][-10:]

        # Update latency stats
        stats["total_latency"] += latency
        stats["min_latency"] = min(stats["min_latency"], latency)
        stats["max_latency"] = max(stats["max_latency"], latency)

        # Update session tracking
        self.session_calls[tool_name]["calls"] += 1
        self.session_calls[tool_name]["time"] += latency

        self._save_analytics()

    def record_value_score(self, tool_name: str, score: float):
        """
        Record user value score for a tool (from feedback).

        Args:
            tool_name: Name of the tool
            score: Value score (0.0-1.0)
        """
        stats = self._get_tool_stats(tool_name)
        stats["value_scores"].append(score)

        # Keep last 50 scores
        if len(stats["value_scores"]) > 50:
            stats["value_scores"] = stats["value_scores"][-50:]

        self._save_analytics()

    def get_tool_metrics(self, tool_name: str) -> Dict[str, Any]:
        """
        Get comprehensive metrics for a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Metrics dictionary
        """
        if tool_name not in self.analytics:
            return {}

        stats = self.analytics[tool_name]

        success_rate = (
            stats["successful_calls"] / stats["total_calls"]
            if stats["total_calls"] > 0
            else 0.0
        )

        avg_latency = (
            stats["total_latency"] / stats["total_calls"]
            if stats["total_calls"] > 0
            else 0.0
        )

        avg_value = (
            sum(stats["value_scores"]) / len(stats["value_scores"])
            if stats["value_scores"]
            else 0.0
        )

        return {
            "tool_name": tool_name,
            "total_calls": stats["total_calls"],
            "success_rate": success_rate,
            "avg_latency": avg_latency,
            "min_latency": stats["min_latency"] if stats["min_latency"] != float('inf') else 0.0,
            "max_latency": stats["max_latency"],
            "avg_value_score": avg_value,
            "recent_errors": stats["errors"][-3:] if stats["errors"] else []
        }

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for all tools.

        Returns:
            Dictionary of tool metrics
        """
        return {
            tool_name: self.get_tool_metrics(tool_name)
            for tool_name in self.analytics.keys()
        }

    def get_tool_rankings(self) -> List[tuple]:
        """
        Get tools ranked by overall performance.

        Returns:
            List of (tool_name, composite_score) tuples
        """
        rankings = []

        for tool_name in self.analytics.keys():
            metrics = self.get_tool_metrics(tool_name)

            # Composite score (0-100)
            # 40% success rate + 30% value + 20% speed + 10% usage
            success_score = metrics["success_rate"] * 40
            value_score = metrics["avg_value_score"] * 30

            # Speed score (faster = better, normalized to 0-20)
            if metrics["avg_latency"] > 0:
                speed_score = min(20, 20 / metrics["avg_latency"])
            else:
                speed_score = 20

            # Usage score (more usage = more valuable)
            usage_score = min(10, (metrics["total_calls"] / 100) * 10)

            composite = success_score + value_score + speed_score + usage_score

            rankings.append((tool_name, composite))

        return sorted(rankings, key=lambda x: x[1], reverse=True)

    def get_optimization_suggestions(self) -> List[str]:
        """
        Get suggestions for optimizing tool usage.

        Returns:
            List of suggestions
        """
        suggestions = []

        for tool_name, stats in self.analytics.items():
            metrics = self.get_tool_metrics(tool_name)

            # Low success rate
            if metrics["success_rate"] < 0.85:
                suggestions.append(
                    f"⚠️ {tool_name}: Low success rate ({metrics['success_rate']:.1%}). "
                    f"Consider adding retries or fallback data sources."
                )

            # High latency
            if metrics["avg_latency"] > 5.0:
                suggestions.append(
                    f"🐌 {tool_name}: Slow average latency ({metrics['avg_latency']:.1f}s). "
                    f"Consider caching or optimization."
                )

            # Low value
            if metrics["avg_value_score"] > 0 and metrics["avg_value_score"] < 0.5:
                suggestions.append(
                    f"📉 {tool_name}: Low user value score ({metrics['avg_value_score']:.1f}). "
                    f"Consider improving output or making optional."
                )

            # Underutilized
            if metrics["total_calls"] < 10 and metrics["avg_value_score"] < 0.3:
                suggestions.append(
                    f"❓ {tool_name}: Rarely used and low value. "
                    f"Consider removing or improving visibility."
                )

        return suggestions

    def get_analytics_report(self) -> str:
        """
        Get formatted analytics report.

        Returns:
            Formatted report string
        """
        report = "=" * 80 + "\n"
        report += "TOOL ANALYTICS & PERFORMANCE REPORT\n"
        report += "=" * 80 + "\n\n"

        # Tool rankings
        report += "Tool Rankings (by composite performance score):\n"
        report += "-" * 80 + "\n"
        for i, (tool_name, score) in enumerate(self.get_tool_rankings(), 1):
            report += f"{i}. {tool_name}: {score:.1f}/100\n"

        report += "\nDetailed Metrics:\n"
        report += "-" * 80 + "\n"

        for tool_name, metrics in sorted(self.get_all_metrics().items()):
            report += f"\n{tool_name}:\n"
            report += f"  Calls: {metrics['total_calls']}\n"
            report += f"  Success Rate: {metrics['success_rate']:.1%}\n"
            report += f"  Avg Latency: {metrics['avg_latency']:.2f}s\n"
            if metrics['avg_value_score'] > 0:
                report += f"  User Value: {metrics['avg_value_score']:.2f}/1.0\n"

        # Optimization suggestions
        suggestions = self.get_optimization_suggestions()
        if suggestions:
            report += "\nOptimization Suggestions:\n"
            report += "-" * 80 + "\n"
            for suggestion in suggestions:
                report += f"{suggestion}\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global analytics instance
_analytics_instance = None


def get_tool_analytics() -> ToolAnalytics:
    """
    Get global tool analytics instance (singleton).

    Returns:
        ToolAnalytics instance
    """
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = ToolAnalytics()
    return _analytics_instance
