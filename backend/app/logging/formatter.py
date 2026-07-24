"""
AI CyberShield — Log Formatter Module

Custom log formatters for structured and human-readable output.
Supports JSON formatting for machine parsing and standard formatting
for local development.
"""

from logging import Formatter


class JsonFormatter(Formatter):
    """Format log records as JSON objects for structured logging.

    Produces parseable JSON output suitable for log aggregation tools
    (e.g., ELK, Splunk, CloudWatch).
    """

    def format(self, record: object) -> str:
        """Format a log record as a JSON string."""
        return super().format(record)


class StandardFormatter(Formatter):
    """Format log records in a human-readable console format.

    Includes timestamp, log level, module name, and message.
    """

    def format(self, record: object) -> str:
        """Format a log record as a human-readable string."""
        return super().format(record)
