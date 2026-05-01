"""
utils.py - Shared utilities for Smart IT Service Desk
"""

import uuid
import re
from datetime import datetime
from functools import reduce
from typing import List, Dict, Any, Iterator, Generator


# ── Custom Exceptions ──────────────────────────────────────────────────────────
class TicketNotFoundError(Exception):
    """Raised when a ticket ID does not exist."""


class DuplicateTicketError(Exception):
    """Raised when a duplicate ticket is detected."""


class InvalidInputError(Exception):
    """Raised when user input fails validation."""


class SLABreachError(Exception):
    """Raised when an SLA threshold is crossed."""


# ── Priority & SLA Maps ────────────────────────────────────────────────────────
PRIORITY_MAP: Dict[str, str] = {
    "server down":        "P1",
    "internet down":      "P2",
    "network":            "P2",
    "laptop slow":        "P3",
    "slow":               "P3",
    "high cpu":           "P3",
    "disk full":          "P3",
    "application crash":  "P3",
    "password reset":     "P4",
    "printer":            "P4",
    "software install":   "P4",
}

SLA_HOURS: Dict[str, int] = {
    "P1": 1,
    "P2": 4,
    "P3": 8,
    "P4": 24,
}

VALID_STATUSES = {"Open", "In Progress", "Resolved", "Closed", "Escalated"}
VALID_PRIORITIES = set(SLA_HOURS.keys())


# ── ID Generator ───────────────────────────────────────────────────────────────
def generate_ticket_id() -> str:
    """Generate a short unique ticket ID."""
    return "TKT-" + str(uuid.uuid4())[:8].upper()


# ── Auto-priority Detector ─────────────────────────────────────────────────────
def detect_priority(description: str, category: str = "") -> str:
    """Infer priority from issue description / category using simple keyword matching."""
    text = (description + " " + category).lower()
    for keyword, priority in PRIORITY_MAP.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return priority
    return "P4"   # default


# ── Date Helpers ───────────────────────────────────────────────────────────────
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_dt(dt_str: str) -> datetime:
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def hours_since(dt_str: str) -> float:
    delta = datetime.now() - parse_dt(dt_str)
    return delta.total_seconds() / 3600


# ── Functional Helpers ─────────────────────────────────────────────────────────
def filter_by_status(tickets: List[Dict], status: str) -> List[Dict]:
    return list(filter(lambda t: t["status"] == status, tickets))


def map_ticket_ids(tickets: List[Dict]) -> List[str]:
    return list(map(lambda t: t["ticket_id"], tickets))


def count_total_priority(tickets: List[Dict], priority: str) -> int:
    return reduce(lambda acc, t: acc + (1 if t["priority"] == priority else 0), tickets, 0)


# ── Iterator / Generator ───────────────────────────────────────────────────────
class TicketIterator:
    """Iterates over a list of ticket dicts."""

    def __init__(self, tickets: List[Dict]):
        self._tickets = tickets
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> Dict:
        if self._index >= len(self._tickets):
            raise StopIteration
        ticket = self._tickets[self._index]
        self._index += 1
        return ticket


def open_ticket_generator(tickets: List[Dict]) -> Generator[Dict, None, None]:
    """Yield only open / in-progress tickets."""
    for ticket in tickets:
        if ticket["status"] in ("Open", "In Progress"):
            yield ticket


# ── Input Validation ───────────────────────────────────────────────────────────
def validate_non_empty(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise InvalidInputError(f"{field} cannot be empty.")
    return value


def validate_priority(priority: str) -> str:
    priority = priority.strip().upper()
    if priority not in VALID_PRIORITIES:
        raise InvalidInputError(f"Priority must be one of {VALID_PRIORITIES}. Got: {priority}")
    return priority


def validate_status(status: str) -> str:
    status = status.strip().title()
    if status not in VALID_STATUSES:
        raise InvalidInputError(f"Status must be one of {VALID_STATUSES}. Got: {status}")
    return status


# ── Display Helper ─────────────────────────────────────────────────────────────
def print_separator(char: str = "─", width: int = 70):
    print(char * width)


def format_ticket(ticket: Dict) -> str:
    lines = [
        f"  Ticket ID   : {ticket.get('ticket_id')}",
        f"  Employee    : {ticket.get('employee_name')}",
        f"  Department  : {ticket.get('department')}",
        f"  Category    : {ticket.get('category')}",
        f"  Priority    : {ticket.get('priority')}",
        f"  Status      : {ticket.get('status')}",
        f"  Description : {ticket.get('description')}",
        f"  Created     : {ticket.get('created_at')}",
    ]
    if ticket.get("resolved_at"):
        lines.append(f"  Resolved    : {ticket.get('resolved_at')}")
    if ticket.get("sla_breached"):
        lines.append("  ⚠️  SLA BREACHED")
    return "\n".join(lines)
