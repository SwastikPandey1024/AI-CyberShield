"""
AI CyberShield — Logger Module

Centralized logger initialization and management.
Configures loggers based on the application settings and logging configuration.
"""

from logging import Logger


def get_logger(name: str) -> Logger:
    """Retrieve a configured logger instance for the given module name.

    Args:
        name: The module or component name (e.g., 'backend.api', 'ml.training').

    Returns:
        A configured Logger instance.
    """
    return Logger(name)
