"""
itil.py - ITIL Workflow Module: Incident, Service Request, Problem, Change, SLA
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from utils import (
    hours_since, SLA_HOURS, now_str,
    SLABreachError, print_separator, open_ticket_generator
)
from logger import itil_logger, sla_logger, log_action

DATA_DIR      = os.path.join(os.path.dirname(__file__), "data")
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")
PROBLEM_THRESHOLD = 5   # occurrences before a Problem Record is raised


# ══════════════════════════════════════════════════════════════════════════════
# SLA Tracker
# ══════════════════════════════════════════════════════════════════════════════
class SLATracker:
    """Tracks SLA compliance for all tickets."""

    def __init__(self, ticket_manager):
        self._tm = ticket_manager

    # ── Core Checks ───────────────────────────────────────────────────────────
    def check_all_slas(self) -> List[Dict]:
        """Return list of breached tickets and log warnings."""
        breached = []
        for ticket in open_ticket_generator(
            [t.to_dict() for t in self._tm.all_tickets()]
        ):
            t_obj = self._tm.get_ticket(ticket["ticket_id"])
            if t_obj.check_sla():
                breached.append(t_obj.to_dict())
                sla_logger.warning(
                    f"SLA BREACH | {t_obj.ticket_id} | {t_obj.priority} | "
                    f"Open for {hours_since(t_obj.created_at):.1f}h "
                    f"(limit {SLA_HOURS[t_obj.priority]}h)"
                )
        self._tm.save_tickets()
        return breached

    def escalate_breached(self) -> List[str]:
        """Escalate SLA-breached tickets to 'Escalated' status."""
        escalated = []
        breached = self.check_all_slas()
        for td in breached:
            try:
                self._tm.update_status(td["ticket_id"], "Escalated")
                itil_logger.warning(f"Escalated ticket {td['ticket_id']} due to SLA breach.")
                escalated.append(td["ticket_id"])
            except Exception as e:
                itil_logger.error(f"Could not escalate {td['ticket_id']}: {e}")
        return escalated

    def display_sla_status(self):
        tickets = self._tm.all_tickets()
        print_separator()
        print("  📋  SLA STATUS REPORT")
        print_separator()
        if not tickets:
            print("  No tickets to evaluate.")
            print_separator()
            return
        for t in tickets:
            if t.status in ("Closed", "Resolved"):
                if t.resolved_at:
                    elapsed = hours_since(t.created_at)
                    # Recalculate from created → resolved
                    from utils import parse_dt
                    delta = parse_dt(t.resolved_at) - parse_dt(t.created_at)
                    elapsed = delta.total_seconds() / 3600
                limit  = SLA_HOURS.get(t.priority, 24)
                met    = "✅ Met" if elapsed <= limit else "❌ Breached"
                print(f"  {t.ticket_id} | {t.priority} | {met} | {elapsed:.1f}h / {limit}h")
            else:
                elapsed = hours_since(t.created_at)
                limit   = SLA_HOURS.get(t.priority, 24)
                remain  = limit - elapsed
                status  = f"⏳ {remain:.1f}h remaining" if remain > 0 else "🔴 BREACHED"
                print(f"  {t.ticket_id} | {t.priority} | {t.status} | {status}")
        print_separator()


# ══════════════════════════════════════════════════════════════════════════════
# Problem Manager  (ITIL Problem Management)
# ══════════════════════════════════════════════════════════════════════════════
class ProblemManager:
    """Detects repeated incidents and auto-raises Problem Records."""

    def __init__(self, ticket_manager):
        self._tm = ticket_manager
        self._problems: List[Dict] = self._load_problems()

    # ── Persistence ───────────────────────────────────────────────────────────
    def _load_problems(self) -> List[Dict]:
        if not os.path.exists(PROBLEMS_FILE):
            return []
        try:
            with open(PROBLEMS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            itil_logger.error(f"Failed to load problems: {e}")
            return []

    def _save_problems(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(PROBLEMS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._problems, f, indent=2)

    # ── Analysis ──────────────────────────────────────────────────────────────
    @log_action(itil_logger)
    def analyze_repeated_issues(self) -> List[Dict]:
        """
        Group all tickets by category and raise a ProblemRecord
        if any category appears >= PROBLEM_THRESHOLD times.
        """
        from collections import Counter
        tickets = self._tm.all_tickets()
        category_counter = Counter(t.category for t in tickets)
        new_problems = []

        for category, count in category_counter.items():
            if count >= PROBLEM_THRESHOLD:
                # Check if problem already exists for this category
                existing = [p for p in self._problems if p["category"] == category]
                if not existing:
                    problem_ticket = self._tm.create_ticket(
                        employee_name="Problem Management",
                        department="IT Operations",
                        description=(
                            f"Recurring issue detected: '{category}' has occurred "
                            f"{count} times. Root cause investigation required."
                        ),
                        category=category,
                        priority="P2",
                        ticket_type="Problem",
                    )
                    record = {
                        "problem_id":  problem_ticket.ticket_id,
                        "category":    category,
                        "occurrences": count,
                        "detected_at": now_str(),
                        "status":      "Under Investigation",
                    }
                    self._problems.append(record)
                    new_problems.append(record)
                    itil_logger.warning(
                        f"Problem Record raised for '{category}' "
                        f"({count} occurrences) → {problem_ticket.ticket_id}"
                    )

        self._save_problems()
        return new_problems

    def display_problems(self):
        print_separator()
        print("  🔵  PROBLEM RECORDS")
        print_separator()
        if not self._problems:
            print("  No problem records found.")
        for p in self._problems:
            print(
                f"  {p['problem_id']} | {p['category']} | "
                f"Occurrences: {p['occurrences']} | {p['status']} | {p['detected_at']}"
            )
        print_separator()


# ══════════════════════════════════════════════════════════════════════════════
# Change Manager  (ITIL Change Management)
# ══════════════════════════════════════════════════════════════════════════════
class ChangeManager:
    """Handles change requests (patches, updates, configuration changes)."""

    CHANGE_TYPES = ["Normal", "Emergency", "Standard"]

    def __init__(self, ticket_manager):
        self._tm = ticket_manager

    @log_action(itil_logger)
    def raise_change_request(
        self,
        employee_name: str,
        department: str,
        description: str,
        change_type: str = "Normal",
    ):
        if change_type not in self.CHANGE_TYPES:
            change_type = "Normal"
        ticket = self._tm.create_ticket(
            employee_name=employee_name,
            department=department,
            description=description,
            category="Change Request",
            priority="P3",
            ticket_type="Change",
            change_type=change_type,
        )
        itil_logger.info(
            f"Change Request {ticket.ticket_id} raised by {employee_name} [{change_type}]"
        )
        return ticket

    def display_changes(self):
        changes = [t for t in self._tm.all_tickets() if t.ticket_type == "Change"]
        print_separator()
        print("  🟢  CHANGE REQUESTS")
        print_separator()
        if not changes:
            print("  No change requests found.")
        for c in changes:
            print(
                f"  {c.ticket_id} | {c.change_type} | {c.status} | "
                f"{c.employee_name} | {c.created_at}"
            )
        print_separator()
