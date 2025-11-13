"""Multi-model provider system with automatic fallback.

Provides enterprise-grade reliability with automatic failover between
Ollama (local), Groq (fast & free), OpenAI (reliable), and Anthropic (best reasoning).
"""

import logging
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelProviderType(Enum):
    """Available model provider types."""
    OLLAMA = "ollama"
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ModelConfig:
    """Configuration for a model provider."""
    provider: ModelProviderType
    model_name: str
    description: str
    priority: int
    requires_api_key: bool
    cost_per_1k_tokens: float = 0.0


class ModelProvider:
    """
    Multi-model provider with automatic fallback.

    Tries providers in order of priority. Falls back automatically
    if primary fails. Tracks success rates and adapts.
    """

    # Available model configurations (priority order)
    AVAILABLE_MODELS = [
        ModelConfig(
            provider=ModelProviderType.OLLAMA,
            model_name="gpt-oss",
            description="Local Ollama - Private, Free, Full Control",
            priority=1,
            requires_api_key=False,
            cost_per_1k_tokens=0.0
        ),
        ModelConfig(
            provider=ModelProviderType.GROQ,
            model_name="llama3-70b-8192",
            description="Groq - Blazing Fast (300+ tok/s), Free Tier",
            priority=2,
            requires_api_key=True,
            cost_per_1k_tokens=0.0  # Free tier
        ),
        ModelConfig(
            provider=ModelProviderType.OPENAI,
            model_name="gpt-4-turbo",
            description="OpenAI - Industry Standard, Most Reliable",
            priority=3,
            requires_api_key=True,
            cost_per_1k_tokens=0.01  # $10 per 1M tokens
        ),
        ModelConfig(
            provider=ModelProviderType.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            description="Anthropic - Superior Reasoning & Analysis",
            priority=4,
            requires_api_key=True,
            cost_per_1k_tokens=0.003  # $3 per 1M tokens
        )
    ]

    def __init__(self):
        """Initialize model provider system."""
        self.provider_stats = {}
        self.current_provider = None
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        for config in self.AVAILABLE_MODELS:
            self.provider_stats[config.provider] = {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "avg_latency": 0.0,
                "last_success": None,
                "last_failure": None
            }

    def get_llm(self, force_provider: Optional[ModelProviderType] = None):
        """
        Get LLM with automatic fallback.

        Args:
            force_provider: Optional specific provider to use

        Returns:
            Configured LLM instance
        """
        if force_provider:
            return self._create_llm(force_provider)

        # Try providers in priority order
        for config in sorted(self.AVAILABLE_MODELS, key=lambda x: x.priority):
            try:
                llm = self._create_llm(config.provider)
                if llm:
                    self.current_provider = config.provider
                    logger.info(f"Using model provider: {config.provider.value} ({config.model_name})")
                    return llm
            except Exception as e:
                logger.warning(f"Failed to initialize {config.provider.value}: {e}")
                self._record_failure(config.provider)
                continue

        raise RuntimeError("All model providers failed to initialize")

    def _create_llm(self, provider_type: ModelProviderType):
        """
        Create LLM instance for specific provider.

        Args:
            provider_type: Provider to create

        Returns:
            LLM instance
        """
        config = next(c for c in self.AVAILABLE_MODELS if c.provider == provider_type)

        if provider_type == ModelProviderType.OLLAMA:
            return self._create_ollama(config)
        elif provider_type == ModelProviderType.GROQ:
            return self._create_groq(config)
        elif provider_type == ModelProviderType.OPENAI:
            return self._create_openai(config)
        elif provider_type == ModelProviderType.ANTHROPIC:
            return self._create_anthropic(config)

        raise ValueError(f"Unknown provider: {provider_type}")

    def _create_ollama(self, config: ModelConfig):
        """Create Ollama LLM."""
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=config.model_name,
                temperature=0
            )
        except Exception as e:
            logger.error(f"Failed to create Ollama: {e}")
            raise

    def _create_groq(self, config: ModelConfig):
        """Create Groq LLM."""
        try:
            import os
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")

            from langchain_groq import ChatGroq
            return ChatGroq(
                groq_api_key=api_key,
                model_name=config.model_name,
                temperature=0
            )
        except ImportError:
            logger.error("langchain-groq not installed. Install: pip install langchain-groq")
            raise
        except Exception as e:
            logger.error(f"Failed to create Groq: {e}")
            raise

    def _create_openai(self, config: ModelConfig):
        """Create OpenAI LLM."""
        try:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                openai_api_key=api_key,
                model_name=config.model_name,
                temperature=0
            )
        except ImportError:
            logger.error("langchain-openai not installed. Install: pip install langchain-openai")
            raise
        except Exception as e:
            logger.error(f"Failed to create OpenAI: {e}")
            raise

    def _create_anthropic(self, config: ModelConfig):
        """Create Anthropic LLM."""
        try:
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")

            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                anthropic_api_key=api_key,
                model=config.model_name,
                temperature=0
            )
        except ImportError:
            logger.error("langchain-anthropic not installed. Install: pip install langchain-anthropic")
            raise
        except Exception as e:
            logger.error(f"Failed to create Anthropic: {e}")
            raise

    def _record_success(self, provider: ModelProviderType, tokens: int = 0, latency: float = 0.0):
        """Record successful provider usage."""
        stats = self.provider_stats[provider]
        stats["attempts"] += 1
        stats["successes"] += 1
        stats["total_tokens"] += tokens
        stats["last_success"] = time.time()

        # Update average latency
        if stats["avg_latency"] == 0:
            stats["avg_latency"] = latency
        else:
            stats["avg_latency"] = (stats["avg_latency"] + latency) / 2

        # Calculate cost
        config = next(c for c in self.AVAILABLE_MODELS if c.provider == provider)
        stats["total_cost"] += (tokens / 1000) * config.cost_per_1k_tokens

    def _record_failure(self, provider: ModelProviderType):
        """Record provider failure."""
        stats = self.provider_stats[provider]
        stats["attempts"] += 1
        stats["failures"] += 1
        stats["last_failure"] = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get provider statistics.

        Returns:
            Dictionary of provider stats
        """
        return {
            "current_provider": self.current_provider.value if self.current_provider else None,
            "providers": {
                provider.value: {
                    **stats,
                    "success_rate": stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0.0
                }
                for provider, stats in self.provider_stats.items()
            }
        }

    def get_status_report(self) -> str:
        """
        Get human-readable status report.

        Returns:
            Formatted status report
        """
        stats = self.get_stats()
        report = "=" * 80 + "\n"
        report += "MODEL PROVIDER STATUS\n"
        report += "=" * 80 + "\n\n"

        report += f"Current Provider: {stats['current_provider']}\n\n"

        report += "Provider Statistics:\n"
        report += "-" * 80 + "\n"

        for provider_name, provider_stats in stats["providers"].items():
            report += f"\n{provider_name.upper()}:\n"
            report += f"  Attempts: {provider_stats['attempts']}\n"
            report += f"  Success Rate: {provider_stats['success_rate']:.1%}\n"
            report += f"  Total Tokens: {provider_stats['total_tokens']:,}\n"
            report += f"  Total Cost: ${provider_stats['total_cost']:.4f}\n"
            report += f"  Avg Latency: {provider_stats['avg_latency']:.2f}s\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global provider instance
_provider_instance = None


def get_model_provider() -> ModelProvider:
    """
    Get global model provider instance (singleton).

    Returns:
        ModelProvider instance
    """
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = ModelProvider()
    return _provider_instance
