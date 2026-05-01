"""
logger.py - Centralized logging module for Smart IT Service Desk
"""

import logging
import os
from datetime import datetime
from functools import wraps

LOG_FILE = os.path.join(os.path.dirname(__file__), "data", "logs.txt")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


# Module-level loggers
ticket_logger   = get_logger("TicketManager")
monitor_logger  = get_logger("Monitor")
sla_logger      = get_logger("SLATracker")
report_logger   = get_logger("ReportGenerator")
itil_logger     = get_logger("ITIL")
system_logger   = get_logger("System")


# ── Decorator ──────────────────────────────────────────────────────────────────
def log_action(logger: logging.Logger):
    """Decorator that logs entry / exit of a function and catches exceptions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"→ Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"✓ {func.__name__} completed successfully")
                return result
            except Exception as exc:
                logger.error(f"✗ {func.__name__} raised {type(exc).__name__}: {exc}")
                raise
        return wrapper
    return decorator
