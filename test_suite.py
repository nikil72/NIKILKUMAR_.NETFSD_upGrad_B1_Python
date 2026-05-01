"""
test_suite.py - Unit Tests for Smart IT Service Desk
Run with: python -m pytest test_suite.py -v
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

import utils
from utils import (
    generate_ticket_id, detect_priority, validate_non_empty,
    validate_priority, validate_status, hours_since, now_str,
    TicketNotFoundError, DuplicateTicketError, InvalidInputError,
    SLA_HOURS, filter_by_status, count_total_priority,
    TicketIterator, open_ticket_generator,
)
from tickets import (
    Ticket, IncidentTicket, ServiceRequest, ProblemRecord,
    ChangeRequest, TicketManager,
)


# ══════════════════════════════════════════════════════════════════════════════
# Helper — Isolated TicketManager with temp directory
# ══════════════════════════════════════════════════════════════════════════════
class TempTicketManager(TicketManager):
    """TicketManager that writes to a temporary directory."""

    def __init__(self, tmp_dir):
        self._tmp_dir = tmp_dir
        # Patch DATA_DIR inside tickets module
        import tickets as t_module
        self._original_data_dir     = t_module.DATA_DIR
        self._original_ticket_file  = t_module.TICKET_FILE
        self._original_backup_file  = t_module.BACKUP_FILE
        t_module.DATA_DIR    = tmp_dir
        t_module.TICKET_FILE = os.path.join(tmp_dir, "tickets.json")
        t_module.BACKUP_FILE = os.path.join(tmp_dir, "backup.csv")
        super().__init__()

    def teardown(self):
        import tickets as t_module
        t_module.DATA_DIR    = self._original_data_dir
        t_module.TICKET_FILE = self._original_ticket_file
        t_module.BACKUP_FILE = self._original_backup_file


# ══════════════════════════════════════════════════════════════════════════════
# 1. Ticket Creation Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestTicketCreation(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = TempTicketManager(self.tmp)

    def tearDown(self):
        self.tm.teardown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_incident_ticket(self):
        t = self.tm.create_ticket(
            "Alice", "IT", "Server is down", "Server Down", ticket_type="Incident"
        )
        self.assertIsInstance(t, IncidentTicket)
        self.assertEqual(t.employee_name, "Alice")
        self.assertEqual(t.status, "Open")
        self.assertTrue(t.ticket_id.startswith("TKT-"))

    def test_create_service_request(self):
        t = self.tm.create_ticket(
            "Bob", "HR", "Need password reset", "Password Reset",
            ticket_type="ServiceRequest"
        )
        self.assertIsInstance(t, ServiceRequest)
        self.assertEqual(t.priority, "P4")

    def test_create_problem_record(self):
        t = self.tm.create_ticket(
            "System", "IT Ops", "Repeated disk full", "Disk Full",
            ticket_type="Problem"
        )
        self.assertIsInstance(t, ProblemRecord)

    def test_create_change_request(self):
        t = self.tm.create_ticket(
            "Admin", "IT", "Apply security patch", "Change Request",
            ticket_type="Change"
        )
        self.assertIsInstance(t, ChangeRequest)

    def test_empty_employee_raises_error(self):
        with self.assertRaises(InvalidInputError):
            self.tm.create_ticket("", "IT", "Some issue", "Other")

    def test_empty_description_raises_error(self):
        with self.assertRaises(InvalidInputError):
            self.tm.create_ticket("Alice", "IT", "   ", "Other")

    def test_ticket_persisted_to_json(self):
        t = self.tm.create_ticket("Carol", "Finance", "Laptop slow", "Laptop Slow")
        import tickets as t_mod
        with open(t_mod.TICKET_FILE, "r") as f:
            data = json.load(f)
        ids = [d["ticket_id"] for d in data]
        self.assertIn(t.ticket_id, ids)

    def test_total_created_counter(self):
        before = Ticket.total_created()
        self.tm.create_ticket("Dave", "HR", "Printer broken", "Printer Failure")
        self.assertEqual(Ticket.total_created(), before + 1)


# ══════════════════════════════════════════════════════════════════════════════
# 2. Priority Logic Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestPriorityLogic(unittest.TestCase):

    def test_server_down_is_p1(self):
        self.assertEqual(detect_priority("server down"), "P1")

    def test_internet_down_is_p2(self):
        self.assertEqual(detect_priority("internet down"), "P2")

    def test_laptop_slow_is_p3(self):
        self.assertEqual(detect_priority("laptop slow"), "P3")

    def test_password_reset_is_p4(self):
        self.assertEqual(detect_priority("password reset"), "P4")

    def test_unknown_defaults_to_p4(self):
        self.assertEqual(detect_priority("random unknown issue xyz"), "P4")

    def test_case_insensitive(self):
        self.assertEqual(detect_priority("SERVER DOWN"), "P1")

    def test_auto_detect_on_ticket_creation(self):
        tmp = tempfile.mkdtemp()
        tm  = TempTicketManager(tmp)
        t = tm.create_ticket("Eve", "IT", "Server is completely down", "Server Down")
        self.assertEqual(t.priority, "P1")
        tm.teardown()
        shutil.rmtree(tmp, ignore_errors=True)

    def test_explicit_priority_overrides_auto(self):
        tmp = tempfile.mkdtemp()
        tm  = TempTicketManager(tmp)
        t = tm.create_ticket("Eve", "IT", "Server is down", "Server Down", priority="P4")
        self.assertEqual(t.priority, "P4")
        tm.teardown()
        shutil.rmtree(tmp, ignore_errors=True)

    def test_invalid_priority_raises_error(self):
        with self.assertRaises(InvalidInputError):
            validate_priority("P9")

    def test_valid_priorities_accepted(self):
        for p in ("P1", "P2", "P3", "P4"):
            self.assertEqual(validate_priority(p), p)


# ══════════════════════════════════════════════════════════════════════════════
# 3. SLA Breach Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestSLABreach(unittest.TestCase):

    def _make_ticket(self, priority, hours_ago):
        t = IncidentTicket(
            employee_name="Test User",
            department="IT",
            description="Test issue",
            category="Other",
            priority=priority,
        )
        past = datetime.now() - timedelta(hours=hours_ago)
        t.created_at = past.strftime("%Y-%m-%d %H:%M:%S")
        return t

    def test_p1_breaches_after_1_hour(self):
        t = self._make_ticket("P1", 2)
        self.assertTrue(t.check_sla())
        self.assertTrue(t.sla_breached)

    def test_p1_no_breach_within_1_hour(self):
        t = self._make_ticket("P1", 0.5)
        self.assertFalse(t.check_sla())

    def test_p4_breaches_after_24_hours(self):
        t = self._make_ticket("P4", 25)
        self.assertTrue(t.check_sla())

    def test_p4_no_breach_at_23_hours(self):
        t = self._make_ticket("P4", 23)
        self.assertFalse(t.check_sla())

    def test_resolved_ticket_no_breach(self):
        t = self._make_ticket("P1", 5)
        t.status = "Resolved"
        self.assertFalse(t.check_sla())

    def test_sla_hours_map(self):
        self.assertEqual(SLA_HOURS["P1"], 1)
        self.assertEqual(SLA_HOURS["P2"], 4)
        self.assertEqual(SLA_HOURS["P3"], 8)
        self.assertEqual(SLA_HOURS["P4"], 24)


# ══════════════════════════════════════════════════════════════════════════════
# 4. Auto Monitoring Ticket Creation Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestAutoMonitoring(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = TempTicketManager(self.tmp)

    def tearDown(self):
        self.tm.teardown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    @patch("monitor.psutil.cpu_percent", return_value=95.0)
    @patch("monitor.psutil.virtual_memory")
    @patch("monitor.psutil.disk_usage")
    @patch("monitor.psutil.net_io_counters")
    def test_high_cpu_creates_p1_ticket(self, mock_net, mock_disk, mock_vm, mock_cpu):
        mock_vm.return_value = MagicMock(percent=50, used=4*1024**3, total=8*1024**3)
        mock_disk.return_value = MagicMock(percent=50, free=100*1024**3, total=200*1024**3)
        mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)

        from monitor import Monitor
        m = Monitor(ticket_manager=self.tm)
        alerts = m.check_and_alert()
        self.assertTrue(any(r == "CPU" for r, _ in alerts))
        cpu_tickets = [t for t in self.tm.all_tickets() if "CPU" in t.category]
        self.assertGreater(len(cpu_tickets), 0)
        self.assertEqual(cpu_tickets[0].priority, "P1")

    @patch("monitor.psutil.cpu_percent", return_value=10.0)
    @patch("monitor.psutil.virtual_memory")
    @patch("monitor.psutil.disk_usage")
    @patch("monitor.psutil.net_io_counters")
    def test_normal_cpu_no_ticket(self, mock_net, mock_disk, mock_vm, mock_cpu):
        mock_vm.return_value = MagicMock(percent=50, used=4*1024**3, total=8*1024**3)
        mock_disk.return_value = MagicMock(percent=50, free=100*1024**3, total=200*1024**3)
        mock_net.return_value = MagicMock(bytes_sent=0, bytes_recv=0)

        from monitor import Monitor
        m = Monitor(ticket_manager=self.tm)
        before_count = len(self.tm.all_tickets())
        m.check_and_alert()
        self.assertEqual(len(self.tm.all_tickets()), before_count)


# ══════════════════════════════════════════════════════════════════════════════
# 5. File Read / Write Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestFileOperations(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = TempTicketManager(self.tmp)

    def tearDown(self):
        self.tm.teardown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tickets_saved_and_reloaded(self):
        self.tm.create_ticket("Frank", "Ops", "Server crash", "Server Down")
        # Create a new manager pointing at the same temp dir — should reload
        tm2 = TempTicketManager(self.tmp)
        self.assertEqual(len(tm2.all_tickets()), len(self.tm.all_tickets()))
        tm2.teardown()

    def test_backup_creates_csv(self):
        self.tm.create_ticket("Grace", "IT", "Printer jam", "Printer Failure")
        import tickets as t_mod
        self.tm.backup_to_csv()
        self.assertTrue(os.path.exists(t_mod.BACKUP_FILE))

    def test_backup_csv_has_correct_rows(self):
        import csv, tickets as t_mod
        self.tm.create_ticket("Hank", "Finance", "Disk full", "Disk Full")
        self.tm.create_ticket("Iris", "HR", "App crash", "Application Crash")
        self.tm.backup_to_csv()
        with open(t_mod.BACKUP_FILE, "r") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)

    def test_json_structure(self):
        t = self.tm.create_ticket("Jane", "Dev", "CPU high", "High CPU")
        import tickets as t_mod
        with open(t_mod.TICKET_FILE, "r") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertIn("ticket_id", data[0])
        self.assertIn("priority", data[0])


# ══════════════════════════════════════════════════════════════════════════════
# 6. Search Ticket Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestTicketSearch(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = TempTicketManager(self.tmp)
        self.t1  = self.tm.create_ticket("Alice", "IT",      "Internet down",  "Internet Down")
        self.t2  = self.tm.create_ticket("Bob",   "Finance", "Laptop slow",    "Laptop Slow")
        self.t3  = self.tm.create_ticket("Alice", "IT",      "Password reset", "Password Reset")

    def tearDown(self):
        self.tm.teardown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_search_by_id_found(self):
        result = self.tm.search_by_id(self.t1.ticket_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.ticket_id, self.t1.ticket_id)

    def test_search_by_id_not_found(self):
        result = self.tm.search_by_id("TKT-ZZZZZZZZ")
        self.assertIsNone(result)

    def test_search_by_employee(self):
        results = self.tm.search_by_employee("Alice")
        self.assertEqual(len(results), 2)

    def test_search_by_status(self):
        self.tm.update_status(self.t2.ticket_id, "Closed")
        closed = self.tm.search_by_status("Closed")
        self.assertGreaterEqual(len(closed), 1)

    def test_sort_by_priority(self):
        sorted_tickets = self.tm.sort_by_priority()
        priorities = [t.priority for t in sorted_tickets]
        # P1 < P2 < P3 < P4 in sort order
        order = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
        nums = [order[p] for p in priorities]
        self.assertEqual(nums, sorted(nums))

    def test_get_ticket_raises_if_missing(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.get_ticket("TKT-MISSING1")


# ══════════════════════════════════════════════════════════════════════════════
# 7. Exception Handling Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestExceptionHandling(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.tm  = TempTicketManager(self.tmp)

    def tearDown(self):
        self.tm.teardown()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_invalid_ticket_id_raises(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.get_ticket("INVALID-ID")

    def test_empty_employee_raises(self):
        with self.assertRaises(InvalidInputError):
            self.tm.create_ticket("", "IT", "Issue", "Other")

    def test_invalid_status_raises(self):
        t = self.tm.create_ticket("Zoe", "IT", "Network issue", "Network")
        with self.assertRaises(InvalidInputError):
            self.tm.update_status(t.ticket_id, "FLYING")

    def test_invalid_priority_string_raises(self):
        with self.assertRaises(InvalidInputError):
            validate_priority("URGENT")

    def test_validate_non_empty_strips_spaces(self):
        result = validate_non_empty("  Alice  ", "Name")
        self.assertEqual(result, "Alice")

    def test_validate_non_empty_blank_raises(self):
        with self.assertRaises(InvalidInputError):
            validate_non_empty("   ", "Field")

    def test_delete_nonexistent_raises(self):
        with self.assertRaises(TicketNotFoundError):
            self.tm.delete_ticket("TKT-NOPE0000")

    def test_close_updates_resolved_at(self):
        t = self.tm.create_ticket("Sam", "HR", "Printer issue", "Printer Failure")
        self.assertIsNone(t.resolved_at)
        self.tm.close_ticket(t.ticket_id)
        self.assertIsNotNone(t.resolved_at)


# ══════════════════════════════════════════════════════════════════════════════
# 8. Iterator / Generator Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestIteratorsGenerators(unittest.TestCase):

    def test_ticket_iterator(self):
        tickets = [{"ticket_id": f"TKT-{i:04d}"} for i in range(3)]
        it = TicketIterator(tickets)
        result = list(it)
        self.assertEqual(len(result), 3)

    def test_open_ticket_generator(self):
        tickets = [
            {"ticket_id": "TKT-0001", "status": "Open"},
            {"ticket_id": "TKT-0002", "status": "Closed"},
            {"ticket_id": "TKT-0003", "status": "In Progress"},
        ]
        open_t = list(open_ticket_generator(tickets))
        self.assertEqual(len(open_t), 2)
        self.assertEqual(open_t[0]["ticket_id"], "TKT-0001")

    def test_filter_by_status(self):
        tickets = [
            {"status": "Open"},
            {"status": "Closed"},
            {"status": "Open"},
        ]
        result = filter_by_status(tickets, "Open")
        self.assertEqual(len(result), 2)

    def test_count_total_priority(self):
        tickets = [
            {"priority": "P1"},
            {"priority": "P1"},
            {"priority": "P2"},
        ]
        self.assertEqual(count_total_priority(tickets, "P1"), 2)
        self.assertEqual(count_total_priority(tickets, "P3"), 0)


# ══════════════════════════════════════════════════════════════════════════════
# 9. OOP / Inheritance Tests
# ══════════════════════════════════════════════════════════════════════════════
class TestOOPInheritance(unittest.TestCase):

    def test_incident_is_ticket(self):
        t = IncidentTicket("Alice", "IT", "Server down", "Server Down")
        self.assertIsInstance(t, Ticket)
        self.assertIsInstance(t, IncidentTicket)

    def test_service_request_is_ticket(self):
        t = ServiceRequest("Bob", "HR", "Password reset", "Password Reset")
        self.assertIsInstance(t, Ticket)

    def test_problem_record_is_ticket(self):
        t = ProblemRecord("Sys", "IT", "Recurrence", "Disk Full")
        self.assertIsInstance(t, Ticket)

    def test_change_request_is_ticket(self):
        t = ChangeRequest("Admin", "IT", "Apply patch", "Change Request")
        self.assertIsInstance(t, Ticket)

    def test_polymorphic_str(self):
        t1 = IncidentTicket("A", "IT", "X", "Y")
        t2 = ServiceRequest("B", "HR", "X", "Y")
        self.assertIn("INCIDENT", str(t1))
        self.assertIn("SERVICE", str(t2))

    def test_to_dict_round_trip(self):
        t = IncidentTicket("Alice", "IT", "Server crash", "Server Down")
        d = t.to_dict()
        t2 = Ticket.from_dict(d)
        self.assertEqual(t.ticket_id, t2.ticket_id)
        self.assertEqual(t.priority, t2.priority)

    def test_equality(self):
        t = IncidentTicket("Alice", "IT", "Crash", "Server Down")
        d = t.to_dict()
        t2 = Ticket.from_dict(d)
        self.assertEqual(t, t2)

    def test_static_sla_hours(self):
        self.assertEqual(Ticket.get_sla_hours("P1"), 1)
        self.assertEqual(Ticket.get_sla_hours("P3"), 8)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    unittest.main(verbosity=2)
