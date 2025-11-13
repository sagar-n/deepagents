"""User feedback system for continuous improvement.

Collects and analyzes user feedback to improve system performance.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FeedbackSystem:
    """
    User feedback collection and analysis system.

    Tracks:
    - Star ratings
    - Helpful/unhelpful aspects
    - Missing information
    - Feature requests
    """

    def __init__(self, feedback_file: str = "user_feedback.json"):
        """
        Initialize feedback system.

        Args:
            feedback_file: Path to feedback storage file
        """
        self.feedback_file = Path(feedback_file)
        self.feedback_data = self._load_feedback()

    def _load_feedback(self) -> Dict[str, Any]:
        """Load feedback from file."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except:
                logger.warning("Failed to load feedback data, starting fresh")

        return {
            "ratings": [],
            "helpful_aspects": {},
            "missing_aspects": {},
            "feature_requests": [],
            "total_feedback": 0,
            "avg_rating": 0.0
        }

    def _save_feedback(self):
        """Save feedback to file."""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")

    def submit_feedback(
        self,
        research_id: int,
        rating: int,
        helpful_aspects: Optional[List[str]] = None,
        missing_aspects: Optional[List[str]] = None,
        comments: Optional[str] = None
    ):
        """
        Submit user feedback for a research report.

        Args:
            research_id: ID of research report
            rating: Star rating (1-5)
            helpful_aspects: List of helpful aspects
            missing_aspects: List of missing/needed aspects
            comments: Free-form comments
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        feedback_entry = {
            "research_id": research_id,
            "rating": rating,
            "helpful_aspects": helpful_aspects or [],
            "missing_aspects": missing_aspects or [],
            "comments": comments,
            "timestamp": datetime.now().isoformat()
        }

        # Add to ratings list
        self.feedback_data["ratings"].append(feedback_entry)

        # Update helpful aspects count
        for aspect in (helpful_aspects or []):
            self.feedback_data["helpful_aspects"][aspect] = \
                self.feedback_data["helpful_aspects"].get(aspect, 0) + 1

        # Update missing aspects count
        for aspect in (missing_aspects or []):
            self.feedback_data["missing_aspects"][aspect] = \
                self.feedback_data["missing_aspects"].get(aspect, 0) + 1

        # Update statistics
        self.feedback_data["total_feedback"] += 1
        all_ratings = [r["rating"] for r in self.feedback_data["ratings"]]
        self.feedback_data["avg_rating"] = sum(all_ratings) / len(all_ratings)

        self._save_feedback()

        logger.info(f"Feedback submitted: {rating} stars for research {research_id}")

    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get feedback summary statistics.

        Returns:
            Summary dictionary
        """
        ratings = [r["rating"] for r in self.feedback_data["ratings"]]

        if not ratings:
            return {
                "total_feedback": 0,
                "avg_rating": 0.0,
                "rating_distribution": {},
                "top_helpful_aspects": [],
                "top_missing_aspects": []
            }

        # Rating distribution
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}

        # Top helpful aspects
        top_helpful = sorted(
            self.feedback_data["helpful_aspects"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Top missing aspects
        top_missing = sorted(
            self.feedback_data["missing_aspects"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_feedback": len(ratings),
            "avg_rating": sum(ratings) / len(ratings),
            "rating_distribution": rating_dist,
            "top_helpful_aspects": top_helpful,
            "top_missing_aspects": top_missing,
            "recent_comments": [
                r.get("comments") for r in self.feedback_data["ratings"][-5:]
                if r.get("comments")
            ]
        }

    def get_improvement_suggestions(self) -> List[str]:
        """
        Get actionable improvement suggestions based on feedback.

        Returns:
            List of suggestions
        """
        summary = self.get_feedback_summary()
        suggestions = []

        # Low rating
        if summary["avg_rating"] < 3.5:
            suggestions.append(
                f"⚠️ Average rating is low ({summary['avg_rating']:.1f}/5). "
                "Review recent feedback for common issues."
            )

        # Most requested missing aspects
        if summary["top_missing_aspects"]:
            top_missing = summary["top_missing_aspects"][0]
            suggestions.append(
                f"🎯 Most requested feature: '{top_missing[0]}' "
                f"(requested {top_missing[1]} times). Consider adding this."
            )

        # High-value aspects
        if summary["top_helpful_aspects"]:
            top_helpful = summary["top_helpful_aspects"][0]
            suggestions.append(
                f"✅ Users love: '{top_helpful[0]}' "
                f"(mentioned {top_helpful[1]} times). Emphasize this more."
            )

        return suggestions

    def get_feedback_report(self) -> str:
        """
        Get formatted feedback report.

        Returns:
            Formatted report string
        """
        summary = self.get_feedback_summary()

        report = "=" * 80 + "\n"
        report += "USER FEEDBACK ANALYSIS\n"
        report += "=" * 80 + "\n\n"

        report += f"Total Feedback Received: {summary['total_feedback']}\n"
        report += f"Average Rating: {summary['avg_rating']:.2f} / 5.0\n\n"

        report += "Rating Distribution:\n"
        for rating in range(5, 0, -1):
            count = summary['rating_distribution'].get(rating, 0)
            bar = "★" * count
            report += f"  {rating} stars: {bar} ({count})\n"

        report += "\nTop Helpful Aspects:\n"
        for aspect, count in summary['top_helpful_aspects']:
            report += f"  • {aspect} ({count} mentions)\n"

        report += "\nMost Requested Missing Aspects:\n"
        for aspect, count in summary['top_missing_aspects']:
            report += f"  • {aspect} ({count} requests)\n"

        suggestions = self.get_improvement_suggestions()
        if suggestions:
            report += "\nActionable Suggestions:\n"
            for suggestion in suggestions:
                report += f"  {suggestion}\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global feedback system instance
_feedback_system = None


def get_feedback_system() -> FeedbackSystem:
    """
    Get global feedback system instance (singleton).

    Returns:
        FeedbackSystem instance
    """
    global _feedback_system
    if _feedback_system is None:
        _feedback_system = FeedbackSystem()
    return _feedback_system
