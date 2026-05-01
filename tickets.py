"""
tickets.py - OOP Ticket classes and TicketManager for Smart IT Service Desk
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

from utils import (
    generate_ticket_id, detect_priority, now_str, hours_since,
    validate_non_empty, validate_priority, validate_status,
    TicketNotFoundError, DuplicateTicketError, InvalidInputError,
    SLA_HOURS, VALID_STATUSES, format_ticket, print_separator, filter_by_status
)
from logger import ticket_logger, log_action

DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
TICKET_FILE = os.path.join(DATA_DIR, "tickets.json")
BACKUP_FILE = os.path.join(DATA_DIR, "backup.csv")


# ══════════════════════════════════════════════════════════════════════════════
# Base Ticket Class
# ══════════════════════════════════════════════════════════════════════════════
class Ticket:
    """Base class representing an IT support ticket."""

    _total_created: int = 0   # class-level counter (encapsulation demo)

    def __init__(
        self,
        employee_name: str,
        department: str,
        description: str,
        category: str,
        priority: Optional[str] = None,
        ticket_id: Optional[str] = None,
        status: str = "Open",
        created_at: Optional[str] = None,
        resolved_at: Optional[str] = None,
        sla_breached: bool = False,
        ticket_type: str = "General",
    ):
        self._ticket_id    = ticket_id or generate_ticket_id()
        self.employee_name = employee_name
        self.department    = department
        self.description   = description
        self.category      = category
        self.priority      = priority or detect_priority(description, category)
        self._status       = status
        self.created_at    = created_at or now_str()
        self.resolved_at   = resolved_at
        self.sla_breached  = sla_breached
        self.ticket_type   = ticket_type
        Ticket._total_created += 1

    # ── Properties (Encapsulation) ────────────────────────────────────────────
    @property
    def ticket_id(self) -> str:
        return self._ticket_id

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        value = validate_status(value)
        if value in ("Resolved", "Closed") and not self.resolved_at:
            self.resolved_at = now_str()
        self._status = value

    # ── Static / Class Methods ────────────────────────────────────────────────
    @staticmethod
    def get_sla_hours(priority: str) -> int:
        return SLA_HOURS.get(priority, 24)

    @classmethod
    def total_created(cls) -> int:
        return cls._total_created

    # ── Special / Dunder Methods ──────────────────────────────────────────────
    def __str__(self) -> str:
        return (
            f"[{self.ticket_type}] {self._ticket_id} | {self.employee_name} | "
            f"{self.priority} | {self._status}"
        )

    def __repr__(self) -> str:
        return f"Ticket(id={self._ticket_id!r}, priority={self.priority!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Ticket):
            return self._ticket_id == other._ticket_id
        return False

    # ── Serialisation ─────────────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id":     self._ticket_id,
            "ticket_type":   self.ticket_type,
            "employee_name": self.employee_name,
            "department":    self.department,
            "description":   self.description,
            "category":      self.category,
            "priority":      self.priority,
            "status":        self._status,
            "created_at":    self.created_at,
            "resolved_at":   self.resolved_at,
            "sla_breached":  self.sla_breached,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        ttype = data.get("ticket_type", "General")
        klass = _TYPE_MAP.get(ttype, cls)
        obj = object.__new__(klass)
        obj._ticket_id    = data["ticket_id"]
        obj.ticket_type   = ttype
        obj.employee_name = data["employee_name"]
        obj.department    = data["department"]
        obj.description   = data["description"]
        obj.category      = data["category"]
        obj.priority      = data["priority"]
        obj._status       = data["status"]
        obj.created_at    = data["created_at"]
        obj.resolved_at   = data.get("resolved_at")
        obj.sla_breached  = data.get("sla_breached", False)
        # subclass-specific fields
        obj.resolution_notes = data.get("resolution_notes", "")
        obj.workaround       = data.get("workaround", "")
        obj.root_cause       = data.get("root_cause", "")
        obj.change_type      = data.get("change_type", "")
        return obj

    # ── SLA Check ─────────────────────────────────────────────────────────────
    def check_sla(self) -> bool:
        if self._status in ("Resolved", "Closed"):
            return False
        hours_elapsed = hours_since(self.created_at)
        limit = self.get_sla_hours(self.priority)
        if hours_elapsed > limit:
            self.sla_breached = True
            return True
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Subclasses (Inheritance + Polymorphism)
# ══════════════════════════════════════════════════════════════════════════════
class IncidentTicket(Ticket):
    """Represents an incident (outage / failure)."""

    def __init__(self, *args, resolution_notes: str = "", **kwargs):
        super().__init__(*args, ticket_type="Incident", **kwargs)
        self.resolution_notes = resolution_notes
        self.workaround       = ""
        self.root_cause       = ""
        self.change_type      = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["resolution_notes"] = self.resolution_notes
        d["workaround"]       = self.workaround
        d["root_cause"]       = self.root_cause
        d["change_type"]      = self.change_type
        return d

    def __str__(self) -> str:
        return f"🔴 INCIDENT  | {super().__str__()}"


class ServiceRequest(Ticket):
    """Represents a standard service request (password reset, etc.)."""

    def __init__(self, *args, workaround: str = "", **kwargs):
        super().__init__(*args, ticket_type="ServiceRequest", **kwargs)
        self.workaround       = workaround
        self.resolution_notes = ""
        self.root_cause       = ""
        self.change_type      = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["workaround"]       = self.workaround
        d["resolution_notes"] = self.resolution_notes
        d["root_cause"]       = self.root_cause
        d["change_type"]      = self.change_type
        return d

    def __str__(self) -> str:
        return f"🟡 SERVICE   | {super().__str__()}"


class ProblemRecord(Ticket):
    """Represents a problem (root-cause investigation)."""

    def __init__(self, *args, root_cause: str = "", **kwargs):
        super().__init__(*args, ticket_type="Problem", **kwargs)
        self.root_cause       = root_cause
        self.resolution_notes = ""
        self.workaround       = ""
        self.change_type      = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["root_cause"]       = self.root_cause
        d["resolution_notes"] = self.resolution_notes
        d["workaround"]       = self.workaround
        d["change_type"]      = self.change_type
        return d

    def __str__(self) -> str:
        return f"🔵 PROBLEM   | {super().__str__()}"


class ChangeRequest(Ticket):
    """Represents a change request (patch, update)."""

    def __init__(self, *args, change_type: str = "Normal", **kwargs):
        super().__init__(*args, ticket_type="Change", **kwargs)
        self.change_type      = change_type
        self.resolution_notes = ""
        self.workaround       = ""
        self.root_cause       = ""

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["change_type"]      = self.change_type
        d["resolution_notes"] = self.resolution_notes
        d["workaround"]       = self.workaround
        d["root_cause"]       = self.root_cause
        return d

    def __str__(self) -> str:
        return f"🟢 CHANGE    | {super().__str__()}"


_TYPE_MAP = {
    "Incident":      IncidentTicket,
    "ServiceRequest": ServiceRequest,
    "Problem":       ProblemRecord,
    "Change":        ChangeRequest,
    "General":       Ticket,
}


# ══════════════════════════════════════════════════════════════════════════════
# Ticket Manager
# ══════════════════════════════════════════════════════════════════════════════
class TicketManager:
    """Central manager for all ticket CRUD operations and persistence."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self._tickets: Dict[str, Ticket] = {}
        self._load_tickets()
        self.backup_to_csv()  # always create/refresh backup.csv on startup

    # ── Persistence ───────────────────────────────────────────────────────────
    def _load_tickets(self):
        if not os.path.exists(TICKET_FILE):
            ticket_logger.info("No existing tickets file – starting fresh.")
            return
        try:
            with open(TICKET_FILE, "r", encoding="utf-8") as f:
                data: List[Dict] = json.load(f)
            for item in data:
                t = Ticket.from_dict(item)
                self._tickets[t.ticket_id] = t
            ticket_logger.info(f"Loaded {len(self._tickets)} tickets from {TICKET_FILE}")
        except (json.JSONDecodeError, KeyError) as e:
            ticket_logger.error(f"Failed to load tickets: {e}")

    @log_action(ticket_logger)
    def save_tickets(self):
        """Persist all tickets to JSON and refresh CSV backup."""
        try:
            with open(TICKET_FILE, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self._tickets.values()], f, indent=2)
            ticket_logger.info(f"Saved {len(self._tickets)} tickets to {TICKET_FILE}")
        except OSError as e:
            ticket_logger.critical(f"Cannot write tickets file: {e}")
            raise
        self.backup_to_csv()  # keep CSV in sync with JSON

    @log_action(ticket_logger)
    def backup_to_csv(self):
        """Backup all tickets to CSV. Always creates the file, even when empty."""
        # Build fieldnames from a dummy ticket if no tickets exist
        FIELDNAMES = [
            "ticket_id", "ticket_type", "employee_name", "department",
            "description", "category", "priority", "status",
            "created_at", "resolved_at", "sla_breached",
            "resolution_notes", "workaround", "root_cause", "change_type",
        ]
        try:
            with open(BACKUP_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
                writer.writeheader()
                for t in self._tickets.values():
                    writer.writerow(t.to_dict())
            count = len(self._tickets)
            ticket_logger.info(f"Backup written to {BACKUP_FILE} ({count} records)")
            if count == 0:
                ticket_logger.warning("Backup created with headers only — no tickets exist yet.")
        except OSError as e:
            ticket_logger.error(f"Backup failed: {e}")
            raise

    # ── CRUD ──────────────────────────────────────────────────────────────────
    @log_action(ticket_logger)
    def create_ticket(
        self,
        employee_name: str,
        department: str,
        description: str,
        category: str,
        priority: Optional[str] = None,
        ticket_type: str = "Incident",
        **kwargs,
    ) -> Ticket:
        employee_name = validate_non_empty(employee_name, "Employee name")
        department    = validate_non_empty(department, "Department")
        description   = validate_non_empty(description, "Description")
        category      = validate_non_empty(category, "Category")
        if priority:
            priority = validate_priority(priority)

        klass = _TYPE_MAP.get(ticket_type, IncidentTicket)
        ticket = klass(
            employee_name=employee_name,
            department=department,
            description=description,
            category=category,
            priority=priority,
            **kwargs,
        )
        self._tickets[ticket.ticket_id] = ticket
        self.save_tickets()
        ticket_logger.info(f"Created ticket {ticket.ticket_id} [{ticket.ticket_type}] P={ticket.priority}")
        return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        ticket = self._tickets.get(ticket_id.strip().upper())
        if not ticket:
            raise TicketNotFoundError(f"Ticket '{ticket_id}' not found.")
        return ticket

    def all_tickets(self) -> List[Ticket]:
        return list(self._tickets.values())

    @log_action(ticket_logger)
    def update_status(self, ticket_id: str, new_status: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        old = ticket.status
        ticket.status = new_status
        self.save_tickets()
        ticket_logger.info(f"Ticket {ticket_id}: {old} → {new_status}")
        return ticket

    @log_action(ticket_logger)
    def close_ticket(self, ticket_id: str) -> Ticket:
        return self.update_status(ticket_id, "Closed")

    @log_action(ticket_logger)
    def delete_ticket(self, ticket_id: str) -> str:
        ticket = self.get_ticket(ticket_id)
        del self._tickets[ticket_id]
        self.save_tickets()
        ticket_logger.warning(f"Ticket {ticket_id} deleted.")
        return ticket_id

    def search_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id.strip().upper())

    def search_by_employee(self, name: str) -> List[Ticket]:
        name = name.lower()
        return [t for t in self._tickets.values() if name in t.employee_name.lower()]

    def search_by_status(self, status: str) -> List[Ticket]:
        return [t for t in self._tickets.values() if t.status == status]

    def sort_by_priority(self) -> List[Ticket]:
        order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        return sorted(self._tickets.values(), key=lambda t: order.get(t.priority, 99))

    # ── Display ───────────────────────────────────────────────────────────────
    def display_all(self):
        if not self._tickets:
            print("  No tickets found.")
            return
        for t in self.sort_by_priority():
            print_separator()
            print(format_ticket(t.to_dict()))
        print_separator()

    def display_ticket(self, ticket_id: str):
        try:
            t = self.get_ticket(ticket_id)
            print_separator()
            print(format_ticket(t.to_dict()))
            print_separator()
        except TicketNotFoundError as e:
            print(f"  ❌ {e}")
