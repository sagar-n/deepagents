"""Circuit breaker pattern for self-healing system.

Implements circuit breaker to prevent cascading failures and enable
automatic recovery. Stops calling failing services temporarily.
"""

import logging
import time
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes to close from half-open
    timeout: float = 60.0       # Seconds before trying again
    expected_exception: type = Exception


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    States:
    - CLOSED: Normal operation, calls go through
    - OPEN: Too many failures, calls rejected immediately
    - HALF_OPEN: Testing if service recovered, limited calls

    Flow:
    CLOSED --(failures)--> OPEN --(timeout)--> HALF_OPEN --(success)--> CLOSED
                                                  |
                                               (failure)
                                                  |
                                                OPEN
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            name: Name of the circuit (for logging)
            config: Optional configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.total_calls = 0
        self.total_failures = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker.

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        self.total_calls += 1

        # Check if circuit is OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN (attempting recovery)")
            else:
                raise CircuitOpenError(f"Circuit breaker {self.name} is OPEN")

        # Try to call function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.config.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.timeout

    def _on_success(self):
        """Handle successful call."""
        self.last_success_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1

            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        else:
            self.failure_count = 0  # Reset failure count on success

    def _on_failure(self):
        """Handle failed call."""
        self.last_failure_time = time.time()
        self.failure_count += 1
        self.total_failures += 1

        if self.state == CircuitState.HALF_OPEN:
            # Failed during recovery attempt
            self._open_circuit()
        elif self.failure_count >= self.config.failure_threshold:
            self._open_circuit()

    def _open_circuit(self):
        """Open the circuit (stop accepting calls)."""
        self.state = CircuitState.OPEN
        self.success_count = 0
        logger.warning(f"Circuit {self.name}: -> OPEN (too many failures)")

    def _close_circuit(self):
        """Close the circuit (resume normal operation)."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit {self.name}: -> CLOSED (recovered successfully)")

    def reset(self):
        """Manually reset circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit {self.name}: Manually reset")

    def get_status(self) -> dict:
        """
        Get circuit breaker status.

        Returns:
            Status dictionary
        """
        success_rate = 1.0 - (self.total_failures / self.total_calls) if self.total_calls > 0 else 1.0

        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "success_rate": success_rate,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time
        }


class CircuitOpenError(Exception):
    """Exception raised when circuit breaker is OPEN."""
    pass


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to add circuit breaker to a function.

    Args:
        name: Circuit breaker name
        config: Optional configuration

    Returns:
        Decorated function
    """
    breaker = CircuitBreaker(name, config)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        # Attach breaker to function for external access
        wrapper.circuit_breaker = breaker
        return wrapper

    return decorator


# Global registry of circuit breakers
_circuit_breakers = {}


def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """
    Get or create circuit breaker by name.

    Args:
        name: Circuit breaker name
        config: Optional configuration

    Returns:
        CircuitBreaker instance
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def get_all_circuit_status() -> dict:
    """
    Get status of all circuit breakers.

    Returns:
        Dictionary of all circuit breaker statuses
    """
    return {
        name: breaker.get_status()
        for name, breaker in _circuit_breakers.items()
    }


def reset_all_circuits():
    """Reset all circuit breakers."""
    for breaker in _circuit_breakers.values():
        breaker.reset()
    logger.info("All circuit breakers reset")
