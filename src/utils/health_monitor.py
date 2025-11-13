"""Health monitoring dashboard for DeepAgents system.

Tracks overall system health, component status, and performance metrics.
"""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime
from collections import deque

from .circuit_breaker import get_all_circuit_status
from .model_provider import get_model_provider
from .memory import get_memory_system
from .database import get_database

logger = logging.getLogger(__name__)


class SystemHealthMonitor:
    """
    Comprehensive system health monitoring.

    Tracks:
    - Model provider health
    - Tool performance
    - Circuit breaker status
    - Memory system stats
    - Database health
    - Overall system status
    """

    def __init__(self):
        """Initialize health monitor."""
        self.start_time = time.time()
        self.health_checks = deque(maxlen=100)  # Last 100 health checks
        self.alerts = deque(maxlen=50)  # Last 50 alerts

    def perform_health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Returns:
            Health check results
        """
        timestamp = time.time()

        health = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "uptime_seconds": timestamp - self.start_time,
            "components": {}
        }

        # Check model provider
        try:
            provider = get_model_provider()
            provider_stats = provider.get_stats()
            health["components"]["model_provider"] = {
                "status": "healthy" if provider_stats["current_provider"] else "degraded",
                "current_provider": provider_stats["current_provider"],
                "details": provider_stats
            }
        except Exception as e:
            health["components"]["model_provider"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self._add_alert("CRITICAL", "Model provider health check failed", str(e))

        # Check circuit breakers
        try:
            circuit_status = get_all_circuit_status()
            open_circuits = [name for name, status in circuit_status.items() if status["state"] == "open"]

            health["components"]["circuit_breakers"] = {
                "status": "healthy" if not open_circuits else "degraded",
                "open_circuits": open_circuits,
                "total_circuits": len(circuit_status),
                "details": circuit_status
            }

            if open_circuits:
                self._add_alert("WARNING", f"Circuit breakers open: {', '.join(open_circuits)}")
        except Exception as e:
            health["components"]["circuit_breakers"] = {
                "status": "unknown",
                "error": str(e)
            }

        # Check memory system
        try:
            memory = get_memory_system()
            health["components"]["memory_system"] = {
                "status": "healthy",
                "session_interactions": memory.short_term.interaction_count,
                "total_analyses": memory.long_term.memory["interaction_history"]["total_queries"]
            }
        except Exception as e:
            health["components"]["memory_system"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check database
        try:
            db = get_database()
            count = db.get_research_count()
            health["components"]["database"] = {
                "status": "healthy",
                "total_records": count
            }
        except Exception as e:
            health["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            self._add_alert("CRITICAL", "Database health check failed", str(e))

        # Overall status
        component_statuses = [comp["status"] for comp in health["components"].values()]
        if "unhealthy" in component_statuses:
            health["overall_status"] = "unhealthy"
        elif "degraded" in component_statuses:
            health["overall_status"] = "degraded"
        else:
            health["overall_status"] = "healthy"

        # Store health check
        self.health_checks.append(health)

        return health

    def _add_alert(self, level: str, message: str, details: str = ""):
        """Add alert to alert queue."""
        alert = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            "details": details
        }
        self.alerts.append(alert)
        logger.warning(f"ALERT [{level}]: {message} - {details}")

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """
        Get recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of recent alerts
        """
        return list(self.alerts)[-limit:]

    def get_health_history(self, limit: int = 20) -> List[Dict]:
        """
        Get health check history.

        Args:
            limit: Maximum number of checks to return

        Returns:
            List of recent health checks
        """
        return list(self.health_checks)[-limit:]

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated system metrics.

        Returns:
            System metrics dictionary
        """
        if not self.health_checks:
            return {}

        recent_checks = list(self.health_checks)[-10:]

        # Calculate averages
        healthy_count = sum(1 for check in recent_checks if check["overall_status"] == "healthy")
        health_rate = healthy_count / len(recent_checks)

        metrics = {
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "total_health_checks": len(self.health_checks),
            "health_rate": health_rate,
            "recent_status": recent_checks[-1]["overall_status"] if recent_checks else "unknown",
            "total_alerts": len(self.alerts),
            "recent_alerts": self.get_recent_alerts(5)
        }

        return metrics

    def get_dashboard_html(self) -> str:
        """
        Generate HTML dashboard.

        Returns:
            HTML dashboard string
        """
        health = self.perform_health_check()
        metrics = self.get_system_metrics()

        # Status colors
        status_colors = {
            "healthy": "🟢",
            "degraded": "🟡",
            "unhealthy": "🔴",
            "unknown": "⚪"
        }

        html = f"""
        <div style="font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 5px;">
            <h2>🏥 System Health Dashboard</h2>

            <div style="margin: 20px 0;">
                <h3>Overall Status: {status_colors.get(health['overall_status'], '⚪')} {health['overall_status'].upper()}</h3>
                <p>Uptime: {metrics.get('uptime_hours', 0):.1f} hours | Health Rate: {metrics.get('health_rate', 0):.1%}</p>
            </div>

            <div style="margin: 20px 0;">
                <h3>Component Status:</h3>
                <ul>
        """

        for name, component in health["components"].items():
            status = component.get("status", "unknown")
            html += f"<li>{status_colors.get(status, '⚪')} {name.replace('_', ' ').title()}: {status.upper()}"

            # Add details
            if "current_provider" in component:
                html += f" (Using: {component['current_provider']})"
            if "open_circuits" in component and component["open_circuits"]:
                html += f" (Open: {', '.join(component['open_circuits'])})"
            if "session_interactions" in component:
                html += f" ({component['session_interactions']} interactions this session)"

            html += "</li>"

        html += """
                </ul>
            </div>
        """

        # Recent alerts
        if metrics.get("recent_alerts"):
            html += """
            <div style="margin: 20px 0;">
                <h3>Recent Alerts:</h3>
                <ul>
            """
            for alert in metrics["recent_alerts"]:
                level_icon = "🔴" if alert["level"] == "CRITICAL" else "🟡"
                html += f"<li>{level_icon} [{alert['level']}] {alert['message']}</li>"

            html += "</ul></div>"

        html += "</div>"

        return html

    def get_status_report(self) -> str:
        """
        Get text-based status report.

        Returns:
            Formatted status report
        """
        health = self.perform_health_check()
        metrics = self.get_system_metrics()

        report = "=" * 80 + "\n"
        report += "SYSTEM HEALTH MONITORING DASHBOARD\n"
        report += "=" * 80 + "\n\n"

        report += f"Overall Status: {health['overall_status'].upper()}\n"
        report += f"Timestamp: {health['datetime']}\n"
        report += f"Uptime: {metrics.get('uptime_hours', 0):.1f} hours\n"
        report += f"Health Rate: {metrics.get('health_rate', 0):.1%}\n\n"

        report += "COMPONENT STATUS:\n"
        report += "-" * 80 + "\n"

        for name, component in health["components"].items():
            report += f"\n{name.replace('_', ' ').title()}:\n"
            report += f"  Status: {component['status'].upper()}\n"

            if "current_provider" in component:
                report += f"  Provider: {component['current_provider']}\n"

            if "open_circuits" in component:
                report += f"  Open Circuits: {len(component['open_circuits'])}\n"

            if "error" in component:
                report += f"  Error: {component['error']}\n"

        # Alerts
        if metrics.get("recent_alerts"):
            report += "\n\nRECENT ALERTS:\n"
            report += "-" * 80 + "\n"
            for alert in metrics["recent_alerts"]:
                report += f"[{alert['level']}] {alert['message']}\n"

        report += "\n" + "=" * 80 + "\n"
        return report


# Global health monitor instance
_health_monitor = None


def get_health_monitor() -> SystemHealthMonitor:
    """
    Get global health monitor instance (singleton).

    Returns:
        SystemHealthMonitor instance
    """
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor()
    return _health_monitor
