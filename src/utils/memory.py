"""A-Mem style dual-layer memory system for DeepAgents.

Implements short-term (working memory) and long-term (learned patterns)
memory inspired by A-Mem architecture. Enables context-aware, adaptive behavior.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path

from .database import get_database

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Short-term working memory for current session.

    Stores:
    - Recent queries and responses
    - User preferences detected this session
    - Symbols analyzed this session
    - Conversation context
    """

    def __init__(self, max_items: int = 50):
        """
        Initialize short-term memory.

        Args:
            max_items: Maximum items to keep in memory
        """
        self.max_items = max_items
        self.queries = deque(maxlen=max_items)
        self.symbols = set()
        self.preferences = {}
        self.session_start = time.time()
        self.interaction_count = 0

    def add_query(self, query: str, response: str, metadata: Optional[Dict] = None):
        """
        Add query-response pair to short-term memory.

        Args:
            query: User query
            response: System response
            metadata: Optional metadata
        """
        self.queries.append({
            "query": query,
            "response": response,
            "metadata": metadata or {},
            "timestamp": time.time()
        })
        self.interaction_count += 1

        # Extract symbols from query
        from .validation import extract_symbols_from_query
        symbols = extract_symbols_from_query(query)
        self.symbols.update(symbols)

        # Detect preferences
        self._detect_preferences(query, response)

    def _detect_preferences(self, query: str, response: str):
        """Detect user preferences from interactions."""
        query_lower = query.lower()

        # Detect focus areas
        if any(word in query_lower for word in ["technical", "chart", "trend", "momentum"]):
            self.preferences["focus_technical"] = self.preferences.get("focus_technical", 0) + 1

        if any(word in query_lower for word in ["fundamental", "earnings", "revenue", "valuation"]):
            self.preferences["focus_fundamental"] = self.preferences.get("focus_fundamental", 0) + 1

        if any(word in query_lower for word in ["risk", "downside", "volatility"]):
            self.preferences["focus_risk"] = self.preferences.get("focus_risk", 0) + 1

        # Detect investment style
        if any(word in query_lower for word in ["growth", "momentum"]):
            self.preferences["style_growth"] = self.preferences.get("style_growth", 0) + 1

        if any(word in query_lower for word in ["value", "undervalued", "cheap"]):
            self.preferences["style_value"] = self.preferences.get("style_value", 0) + 1

        # Detect time horizon
        if any(word in query_lower for word in ["short term", "trading", "swing"]):
            self.preferences["horizon_short"] = self.preferences.get("horizon_short", 0) + 1

        if any(word in query_lower for word in ["long term", "invest", "hold"]):
            self.preferences["horizon_long"] = self.preferences.get("horizon_long", 0) + 1

    def get_context(self) -> Dict[str, Any]:
        """
        Get current session context.

        Returns:
            Context dictionary
        """
        return {
            "recent_queries": list(self.queries)[-5:],  # Last 5 interactions
            "session_symbols": list(self.symbols),
            "detected_preferences": self.preferences,
            "session_duration": time.time() - self.session_start,
            "interaction_count": self.interaction_count
        }

    def get_recent_symbols(self, limit: int = 10) -> List[str]:
        """Get recently analyzed symbols."""
        return list(self.symbols)[-limit:]

    def clear(self):
        """Clear short-term memory."""
        self.queries.clear()
        self.symbols.clear()
        self.preferences.clear()
        self.session_start = time.time()
        self.interaction_count = 0


class LongTermMemory:
    """
    Long-term persistent memory for learned patterns.

    Stores:
    - Historical interaction patterns
    - Validated preferences
    - Successful strategies
    - User portfolio context
    """

    def __init__(self):
        """Initialize long-term memory."""
        self.db = get_database()
        self.memory_file = Path("long_term_memory.json")
        self.memory = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        """Load long-term memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                logger.warning("Failed to load long-term memory, starting fresh")

        return {
            "user_preferences": {},
            "successful_patterns": [],
            "portfolio_context": {},
            "learned_insights": {},
            "interaction_history": {
                "total_queries": 0,
                "symbols_analyzed": {},
                "query_types": defaultdict(int)
            }
        }

    def _save_memory(self):
        """Save long-term memory to file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save long-term memory: {e}")

    def consolidate_from_short_term(self, short_term: ShortTermMemory):
        """
        Consolidate learnings from short-term to long-term memory.

        Args:
            short_term: Short-term memory to consolidate
        """
        # Update interaction stats
        self.memory["interaction_history"]["total_queries"] += short_term.interaction_count

        # Update symbol frequency
        for symbol in short_term.symbols:
            self.memory["interaction_history"]["symbols_analyzed"][symbol] = \
                self.memory["interaction_history"]["symbols_analyzed"].get(symbol, 0) + 1

        # Consolidate preferences (with validation - need multiple sessions)
        for pref_key, count in short_term.preferences.items():
            if count >= 2:  # Appeared at least twice in session
                current = self.memory["user_preferences"].get(pref_key, 0)
                self.memory["user_preferences"][pref_key] = current + count

        self._save_memory()

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get user profile from long-term memory.

        Returns:
            User profile dictionary
        """
        # Determine dominant preferences
        prefs = self.memory["user_preferences"]

        profile = {
            "dominant_focus": self._get_dominant_key(prefs, ["focus_technical", "focus_fundamental", "focus_risk"]),
            "investment_style": self._get_dominant_key(prefs, ["style_growth", "style_value"]),
            "time_horizon": self._get_dominant_key(prefs, ["horizon_short", "horizon_long"]),
            "frequently_analyzed": self._get_top_symbols(10),
            "total_analyses": self.memory["interaction_history"]["total_queries"]
        }

        return profile

    def _get_dominant_key(self, prefs: Dict, keys: List[str]) -> Optional[str]:
        """Get dominant preference from list of keys."""
        relevant = {k: prefs.get(k, 0) for k in keys}
        if not relevant or max(relevant.values()) == 0:
            return None
        return max(relevant, key=relevant.get)

    def _get_top_symbols(self, limit: int = 10) -> List[tuple]:
        """Get most frequently analyzed symbols."""
        symbols = self.memory["interaction_history"]["symbols_analyzed"]
        return sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:limit]

    def add_successful_pattern(self, pattern: Dict[str, Any]):
        """
        Record a successful analysis pattern.

        Args:
            pattern: Pattern that led to good outcome
        """
        pattern["timestamp"] = datetime.now().isoformat()
        self.memory["successful_patterns"].append(pattern)

        # Keep only last 100 patterns
        if len(self.memory["successful_patterns"]) > 100:
            self.memory["successful_patterns"] = self.memory["successful_patterns"][-100:]

        self._save_memory()

    def update_portfolio_context(self, holdings: List[str]):
        """
        Update user's portfolio context.

        Args:
            holdings: List of symbols in portfolio
        """
        self.memory["portfolio_context"]["holdings"] = holdings
        self.memory["portfolio_context"]["updated_at"] = datetime.now().isoformat()
        self._save_memory()

    def get_recommendations_context(self) -> Dict[str, Any]:
        """
        Get context for making personalized recommendations.

        Returns:
            Recommendation context
        """
        profile = self.get_user_profile()

        context = {
            "user_profile": profile,
            "portfolio_holdings": self.memory["portfolio_context"].get("holdings", []),
            "recent_patterns": self.memory["successful_patterns"][-5:],
            "suggested_adjustments": []
        }

        # Add suggestions based on profile
        if profile["dominant_focus"] == "focus_technical":
            context["suggested_adjustments"].append("Emphasize technical analysis and chart patterns")

        if profile["investment_style"] == "style_growth":
            context["suggested_adjustments"].append("Prioritize growth metrics and momentum")

        if profile["time_horizon"] == "horizon_short":
            context["suggested_adjustments"].append("Focus on short-term catalysts and trading signals")

        return context


class AdaptiveMemorySystem:
    """
    A-Mem style adaptive memory system.

    Combines short-term working memory with long-term learned patterns
    for context-aware, personalized analysis.
    """

    def __init__(self):
        """Initialize adaptive memory system."""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()

    def record_interaction(self, query: str, response: str, metadata: Optional[Dict] = None):
        """
        Record user interaction in memory.

        Args:
            query: User query
            response: System response
            metadata: Optional metadata
        """
        self.short_term.add_query(query, response, metadata)

    def get_context_for_query(self, query: str) -> Dict[str, Any]:
        """
        Get full context for answering a query.

        Args:
            query: Current user query

        Returns:
            Complete context including short-term and long-term memory
        """
        context = {
            "current_session": self.short_term.get_context(),
            "user_profile": self.long_term.get_user_profile(),
            "recommendations": self.long_term.get_recommendations_context(),
            "query": query
        }

        return context

    def consolidate_session(self):
        """Consolidate short-term learnings into long-term memory."""
        self.long_term.consolidate_from_short_term(self.short_term)

    def end_session(self):
        """End session and consolidate memory."""
        self.consolidate_session()
        self.short_term.clear()

    def get_status_report(self) -> str:
        """
        Get memory system status report.

        Returns:
            Formatted status report
        """
        profile = self.long_term.get_user_profile()
        session = self.short_term.get_context()

        report = "=" * 80 + "\n"
        report += "ADAPTIVE MEMORY SYSTEM STATUS\n"
        report += "=" * 80 + "\n\n"

        report += "SHORT-TERM MEMORY (Current Session):\n"
        report += f"  Session Duration: {session['session_duration']:.1f}s\n"
        report += f"  Interactions: {session['interaction_count']}\n"
        report += f"  Symbols Analyzed: {', '.join(session['session_symbols'][-5:]) if session['session_symbols'] else 'None'}\n"
        report += f"  Detected Preferences: {list(session['detected_preferences'].keys())}\n\n"

        report += "LONG-TERM MEMORY (Learned Patterns):\n"
        report += f"  Total Analyses: {profile['total_analyses']}\n"
        report += f"  Dominant Focus: {profile['dominant_focus'] or 'Not determined'}\n"
        report += f"  Investment Style: {profile['investment_style'] or 'Not determined'}\n"
        report += f"  Time Horizon: {profile['time_horizon'] or 'Not determined'}\n"

        if profile['frequently_analyzed']:
            report += f"  Top Symbols: {', '.join([s[0] for s in profile['frequently_analyzed'][:5]])}\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global memory instance
_memory_instance = None


def get_memory_system() -> AdaptiveMemorySystem:
    """
    Get global memory system instance (singleton).

    Returns:
        AdaptiveMemorySystem instance
    """
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = AdaptiveMemorySystem()
    return _memory_instance
