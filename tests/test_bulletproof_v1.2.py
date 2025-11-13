"""Integration tests for bulletproof v1.2.0 features."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestBulletproofSystems:
    """Test all bulletproof v1.2.0 systems."""

    def test_model_provider_initialization(self):
        """Test model provider can be initialized."""
        from src.utils.model_provider import get_model_provider

        provider = get_model_provider()
        assert provider is not None
        assert hasattr(provider, 'get_model')
        assert hasattr(provider, 'get_stats')

    def test_memory_system_initialization(self):
        """Test memory system can be initialized."""
        from src.utils.memory import get_memory_system

        memory = get_memory_system()
        assert memory is not None
        assert hasattr(memory, 'short_term')
        assert hasattr(memory, 'long_term')

    def test_circuit_breaker_creation(self):
        """Test circuit breaker can be created."""
        from src.utils.circuit_breaker import CircuitBreaker, CircuitState

        breaker = CircuitBreaker("test")
        assert breaker is not None
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_health_monitor_initialization(self):
        """Test health monitor can be initialized."""
        from src.utils.health_monitor import get_health_monitor

        monitor = get_health_monitor()
        assert monitor is not None
        assert hasattr(monitor, 'perform_health_check')

    def test_feedback_system_initialization(self):
        """Test feedback system can be initialized."""
        from src.utils.feedback import get_feedback_system

        feedback = get_feedback_system()
        assert feedback is not None
        assert hasattr(feedback, 'submit_feedback')
        assert hasattr(feedback, 'get_feedback_summary')

    def test_analytics_initialization(self):
        """Test analytics system can be initialized."""
        from src.utils.analytics import get_tool_analytics

        analytics = get_tool_analytics()
        assert analytics is not None
        assert hasattr(analytics, 'record_call')
        assert hasattr(analytics, 'get_all_stats')

    def test_confidence_scorer_initialization(self):
        """Test confidence scorer can be initialized."""
        from src.utils.confidence import get_confidence_scorer

        scorer = get_confidence_scorer()
        assert scorer is not None
        assert hasattr(scorer, 'calculate_confidence')

    def test_reflection_agent_structure(self):
        """Test reflection agent is properly structured."""
        from src.agents.reflection import reflection_agent

        assert isinstance(reflection_agent, dict)
        assert 'name' in reflection_agent
        assert 'description' in reflection_agent
        assert 'prompt' in reflection_agent
        assert reflection_agent['name'] == 'reflection-agent'

    def test_memory_interactions(self):
        """Test memory system can store and retrieve interactions."""
        from src.utils.memory import AdaptiveMemorySystem

        memory = AdaptiveMemorySystem()

        # Add interaction
        memory.add_interaction("Test query", "Test response", "user")

        # Check short-term storage
        recent = memory.short_term.get_recent_context(limit=1)
        assert len(recent) >= 1
        assert "Test query" in recent[0]

    def test_confidence_calculation(self):
        """Test confidence scoring calculation."""
        from src.utils.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()

        # Sample data
        data = {
            "stock_price": {"pe_ratio": 25},
            "financials": {"profit_margin": 20},
            "technical": {"trend_signal": "bullish"},
            "news": "Positive news",
            "analysts": {"recommendation_key": "buy"}
        }

        analysis = "Strong buy recommendation. All agents agree on bullish outlook."

        confidence = scorer.calculate_confidence(data, analysis, "AAPL")

        assert confidence is not None
        assert "overall_score" in confidence
        assert "confidence_level" in confidence
        assert 0 <= confidence["overall_score"] <= 1
        assert confidence["confidence_level"] in ["HIGH", "MODERATE", "LOW"]

    def test_circuit_breaker_state_transitions(self):
        """Test circuit breaker state transitions."""
        from src.utils.circuit_breaker import (
            CircuitBreaker,
            CircuitState,
            CircuitBreakerConfig,
            CircuitOpenError
        )

        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)
        breaker = CircuitBreaker("test", config)

        # Initially CLOSED
        assert breaker.state == CircuitState.CLOSED

        # Simulate failures
        def failing_function():
            raise Exception("Test failure")

        # First failure
        with pytest.raises(Exception):
            breaker.call(failing_function)
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 1

        # Second failure - should open circuit
        with pytest.raises(Exception):
            breaker.call(failing_function)
        assert breaker.state == CircuitState.OPEN
        assert breaker.failure_count == 2

        # Third call should be rejected immediately
        with pytest.raises(CircuitOpenError):
            breaker.call(failing_function)

    def test_analytics_recording(self):
        """Test analytics can record tool calls."""
        from src.utils.analytics import ToolAnalytics

        analytics = ToolAnalytics()

        # Record successful call
        analytics.record_call("test_tool", True, 0.5)

        stats = analytics.get_all_stats()
        assert "test_tool" in stats
        assert stats["test_tool"]["total_calls"] == 1
        assert stats["test_tool"]["success_rate"] == 1.0

        # Record failed call
        analytics.record_call("test_tool", False, 1.0, "Test error")

        stats = analytics.get_all_stats()
        assert stats["test_tool"]["total_calls"] == 2
        assert stats["test_tool"]["success_rate"] == 0.5

    def test_feedback_submission(self):
        """Test feedback submission."""
        from src.utils.feedback import FeedbackSystem

        feedback = FeedbackSystem()

        # Submit feedback
        feedback.submit_feedback(
            research_id=1,
            rating=5,
            helpful_aspects=["clear", "comprehensive"],
            missing_aspects=[]
        )

        # Get summary
        summary = feedback.get_feedback_summary()
        assert summary["total_feedback"] == 1
        assert summary["average_rating"] == 5.0
        assert 5 in summary["rating_distribution"]

    def test_health_check_structure(self):
        """Test health check returns proper structure."""
        from src.utils.health_monitor import HealthMonitor

        monitor = HealthMonitor()
        health = monitor.perform_health_check()

        assert "status" in health
        assert "timestamp" in health
        assert "components" in health
        assert "uptime_seconds" in health

        # Check component structure
        assert isinstance(health["components"], dict)

    def test_model_provider_fallback_chain(self):
        """Test model provider has fallback chain configured."""
        from src.utils.model_provider import ModelProvider, ModelProviderType

        provider = ModelProvider()

        # Check available models exist
        assert len(provider.AVAILABLE_MODELS) >= 4

        # Check priority order
        priorities = [m.priority for m in provider.AVAILABLE_MODELS]
        assert priorities == sorted(priorities)

        # Check providers are diverse
        provider_types = {m.provider for m in provider.AVAILABLE_MODELS}
        assert ModelProviderType.OLLAMA in provider_types
        assert ModelProviderType.GROQ in provider_types or ModelProviderType.OPENAI in provider_types


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_main_imports(self):
        """Test main.py imports all required modules."""
        # Just try to import main - if it works, all imports are valid
        try:
            from src import main
            assert hasattr(main, 'create_research_agent')
            assert hasattr(main, 'run_stock_research')
            assert hasattr(main, 'get_system_health')
            assert hasattr(main, 'submit_feedback')
        except Exception as e:
            pytest.fail(f"Failed to import main: {e}")

    def test_ui_imports(self):
        """Test UI imports all required modules."""
        try:
            from src.ui import gradio_app_v3
            assert hasattr(gradio_app_v3, 'create_gradio_interface_v2')
        except Exception as e:
            pytest.fail(f"Failed to import UI: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
