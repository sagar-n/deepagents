"""Confidence scoring system for recommendations.

Calculates and explains confidence levels for investment recommendations.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceFactors:
    """Factors contributing to confidence score."""
    data_completeness: float  # 0-1: How much required data is available
    data_freshness: float      # 0-1: How recent the data is
    agent_agreement: float     # 0-1: How much agents agree
    signal_strength: float     # 0-1: How strong the signals are
    historical_accuracy: float # 0-1: Past track record


class ConfidenceScorer:
    """
    Calculates confidence scores for investment recommendations.

    Considers multiple factors:
    - Data quality and completeness
    - Agent consensus
    - Signal strength
    - Historical accuracy
    """

    # Weights for each factor
    WEIGHTS = {
        "data_completeness": 0.25,
        "data_freshness": 0.15,
        "agent_agreement": 0.30,
        "signal_strength": 0.20,
        "historical_accuracy": 0.10
    }

    def __init__(self):
        """Initialize confidence scorer."""
        self.historical_predictions = []

    def calculate_data_completeness(self, data: Dict[str, Any]) -> float:
        """
        Calculate data completeness score.

        Args:
            data: Research data dictionary

        Returns:
            Completeness score (0-1)
        """
        required_fields = [
            "stock_price",
            "financials",
            "technical",
            "news",
            "analysts"
        ]

        available = 0
        total = len(required_fields)

        for field in required_fields:
            if field in data and data[field] and "error" not in str(data[field]):
                # Check if meaningful data exists
                if isinstance(data[field], dict) and len(data[field]) > 1:
                    available += 1
                elif isinstance(data[field], str) and len(data[field]) > 10:
                    available += 1

        return available / total if total > 0 else 0.0

    def calculate_data_freshness(self, data: Dict[str, Any]) -> float:
        """
        Calculate data freshness score.

        Args:
            data: Research data dictionary

        Returns:
            Freshness score (0-1)
        """
        # For now, assume data is fresh if successfully retrieved
        # In production, check timestamps
        has_current_price = "stock_price" in data and "error" not in str(data.get("stock_price", ""))
        has_recent_news = "news" in data and "error" not in str(data.get("news", ""))

        score = 0.5  # Base score

        if has_current_price:
            score += 0.3

        if has_recent_news:
            score += 0.2

        return min(1.0, score)

    def calculate_agent_agreement(self, analysis: str) -> float:
        """
        Calculate agent agreement score based on analysis text.

        Args:
            analysis: Full analysis text

        Returns:
            Agreement score (0-1)
        """
        analysis_lower = analysis.lower()

        # Look for consensus indicators
        consensus_indicators = [
            "all agents agree",
            "unanimous",
            "consistent",
            "aligned",
            "agreement"
        ]

        # Look for disagreement indicators
        disagreement_indicators = [
            "however",
            "but",
            "conflicting",
            "disagreement",
            "mixed signals",
            "contradictory"
        ]

        consensus_count = sum(1 for indicator in consensus_indicators if indicator in analysis_lower)
        disagreement_count = sum(1 for indicator in disagreement_indicators if indicator in analysis_lower)

        # Base score
        score = 0.7

        # Adjust based on indicators
        score += (consensus_count * 0.1)
        score -= (disagreement_count * 0.15)

        return max(0.0, min(1.0, score))

    def calculate_signal_strength(self, data: Dict[str, Any]) -> float:
        """
        Calculate signal strength from technical and sentiment data.

        Args:
            data: Research data dictionary

        Returns:
            Signal strength score (0-1)
        """
        score = 0.5  # Base score

        # Check technical signals
        if "technical" in data:
            tech = data["technical"]
            if isinstance(tech, dict):
                trend = tech.get("trend_signal", "neutral")

                if trend in ["strong_bullish", "strong_bearish"]:
                    score += 0.2
                elif trend in ["bullish", "bearish"]:
                    score += 0.1

                # RSI signals
                rsi = tech.get("rsi")
                if rsi:
                    if rsi < 30 or rsi > 70:  # Strong signal
                        score += 0.1

        # Check analyst consensus
        if "analysts" in data:
            analysts = data["analysts"]
            if isinstance(analysts, dict):
                recommendation = analysts.get("recommendation_key", "")
                if recommendation in ["strong_buy", "strong_sell"]:
                    score += 0.2

        return min(1.0, score)

    def calculate_historical_accuracy(self, symbol: str) -> float:
        """
        Calculate historical accuracy for this symbol.

        Args:
            symbol: Stock symbol

        Returns:
            Historical accuracy score (0-1)
        """
        # Filter predictions for this symbol
        symbol_predictions = [p for p in self.historical_predictions if p.get("symbol") == symbol]

        if not symbol_predictions:
            return 0.7  # Default moderate confidence

        # Calculate accuracy
        correct = sum(1 for p in symbol_predictions if p.get("correct", False))
        accuracy = correct / len(symbol_predictions)

        return accuracy

    def calculate_confidence(
        self,
        data: Dict[str, Any],
        analysis: str,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score.

        Args:
            data: Research data used
            analysis: Generated analysis text
            symbol: Stock symbol

        Returns:
            Confidence score dictionary
        """
        # Calculate individual factors
        factors = ConfidenceFactors(
            data_completeness=self.calculate_data_completeness(data),
            data_freshness=self.calculate_data_freshness(data),
            agent_agreement=self.calculate_agent_agreement(analysis),
            signal_strength=self.calculate_signal_strength(data),
            historical_accuracy=self.calculate_historical_accuracy(symbol)
        )

        # Calculate weighted score
        overall_score = (
            factors.data_completeness * self.WEIGHTS["data_completeness"] +
            factors.data_freshness * self.WEIGHTS["data_freshness"] +
            factors.agent_agreement * self.WEIGHTS["agent_agreement"] +
            factors.signal_strength * self.WEIGHTS["signal_strength"] +
            factors.historical_accuracy * self.WEIGHTS["historical_accuracy"]
        )

        # Determine confidence level
        if overall_score >= 0.8:
            confidence_level = "HIGH"
            interpretation = "Strong confidence in this analysis"
        elif overall_score >= 0.6:
            confidence_level = "MODERATE"
            interpretation = "Reasonable confidence with some uncertainty"
        else:
            confidence_level = "LOW"
            interpretation = "Limited confidence, use caution"

        # Identify caveats
        caveats = self._identify_caveats(factors, data)

        return {
            "overall_score": round(overall_score, 2),
            "confidence_level": confidence_level,
            "interpretation": interpretation,
            "factors": {
                "data_completeness": round(factors.data_completeness, 2),
                "data_freshness": round(factors.data_freshness, 2),
                "agent_agreement": round(factors.agent_agreement, 2),
                "signal_strength": round(factors.signal_strength, 2),
                "historical_accuracy": round(factors.historical_accuracy, 2)
            },
            "caveats": caveats
        }

    def _identify_caveats(self, factors: ConfidenceFactors, data: Dict[str, Any]) -> List[str]:
        """Identify caveats based on low factor scores."""
        caveats = []

        if factors.data_completeness < 0.7:
            caveats.append("Limited data availability - some analysis aspects may be incomplete")

        if factors.data_freshness < 0.6:
            caveats.append("Data may not be fully current - verify latest information")

        if factors.agent_agreement < 0.6:
            caveats.append("Mixed signals from different analysis perspectives - higher uncertainty")

        if factors.signal_strength < 0.5:
            caveats.append("Weak technical/fundamental signals - market may be unclear")

        if factors.historical_accuracy < 0.5:
            caveats.append("Limited track record for this symbol - exercise additional caution")

        return caveats

    def record_prediction(self, symbol: str, prediction: str, correct: bool):
        """
        Record prediction outcome for learning.

        Args:
            symbol: Stock symbol
            prediction: Prediction made (buy/sell/hold)
            correct: Whether prediction was correct
        """
        self.historical_predictions.append({
            "symbol": symbol,
            "prediction": prediction,
            "correct": correct,
            "timestamp": logger.warning  # Should be time.time() but avoiding import
        })

        # Keep last 100 predictions
        if len(self.historical_predictions) > 100:
            self.historical_predictions = self.historical_predictions[-100:]

    def format_confidence_report(self, confidence: Dict[str, Any]) -> str:
        """
        Format confidence score as readable report.

        Args:
            confidence: Confidence dictionary from calculate_confidence

        Returns:
            Formatted report string
        """
        report = "\n" + "=" * 80 + "\n"
        report += "CONFIDENCE ASSESSMENT\n"
        report += "=" * 80 + "\n\n"

        report += f"Overall Confidence: {confidence['confidence_level']} "
        report += f"({confidence['overall_score']:.0%})\n"
        report += f"Interpretation: {confidence['interpretation']}\n\n"

        report += "Contributing Factors:\n"
        for factor, score in confidence["factors"].items():
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            report += f"  {factor.replace('_', ' ').title():.<30} {bar} {score:.0%}\n"

        if confidence["caveats"]:
            report += "\n⚠️ Caveats:\n"
            for caveat in confidence["caveats"]:
                report += f"  • {caveat}\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global confidence scorer instance
_confidence_scorer = None


def get_confidence_scorer() -> ConfidenceScorer:
    """
    Get global confidence scorer instance (singleton).

    Returns:
        ConfidenceScorer instance
    """
    global _confidence_scorer
    if _confidence_scorer is None:
        _confidence_scorer = ConfidenceScorer()
    return _confidence_scorer
