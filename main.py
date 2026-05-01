"""
main.py - Smart IT Service Desk — Interactive CLI with rich UI
"""

import os
import sys
from datetime import datetime

from tickets import TicketManager
from monitor import Monitor
from itil import SLATracker, ProblemManager, ChangeManager
from reports import ReportGenerator
from utils import InvalidInputError, TicketNotFoundError, VALID_STATUSES, validate_non_empty
from logger import system_logger
import ui

# ── Bootstrap ──────────────────────────────────────────────────────────────────
tm      = TicketManager()
monitor = Monitor(ticket_manager=tm)
sla     = SLATracker(tm)
problem = ProblemManager(tm)
change  = ChangeManager(tm)
rpt     = ReportGenerator(tm)

CATEGORIES = [
    "Server Down", "Internet Down", "Network", "Laptop Slow",
    "High CPU", "Disk Full", "Application Crash", "Password Reset",
    "Printer Failure", "Software Install", "Other",
]

TICKET_TYPES = {
    "1": ("Incident",       "Outage / Failure"),
    "2": ("ServiceRequest", "Password reset, installs"),
    "3": ("Change",         "Patch / update / config"),
    "4": ("Problem",        "Root-cause investigation"),
}


# ══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════
def main_menu() -> str:
    ui.print_banner()
    # Quick stats strip
    all_t  = tm.all_tickets()
    open_n = sum(1 for t in all_t if t.status == "Open")
    p1_n   = sum(1 for t in all_t if t.priority == "P1" and t.status not in ("Closed","Resolved"))
    print(ui.c(
        f"  Tickets: {len(all_t)} total  ·  {open_n} open  ·  {p1_n} critical (P1 open)",
        ui.DIM
    ))
    print()
    return ui.print_menu("MAIN MENU", [
        ("1", "Ticket Management"),
        ("2", "System Monitor"),
        ("3", "SLA Management"),
        ("4", "Problem Management  (ITIL)"),
        ("5", "Change Management   (ITIL)"),
        ("6", "Reports"),
        ("7", "Backup to CSV"),
        ("0", ui.c("Exit", ui.BRED)),
    ], color=ui.BCYAN)


# ══════════════════════════════════════════════════════════════════════════════
# TICKET MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
def ticket_menu():
    while True:
        choice = ui.print_menu("TICKET MANAGEMENT", [
            ("1", "Create Ticket"),
            ("2", "View All Tickets"),
            ("3", "Search by Ticket ID"),
            ("4", "Search by Employee Name"),
            ("5", "Update Ticket Status"),
            ("6", "Close Ticket"),
            ("7", "Delete Ticket"),
            ("8", "Filter by Status"),
            ("0", "Back"),
        ], color=ui.BBLUE)

        if choice == "1":
            create_ticket_flow()
        elif choice == "2":
            view_all_tickets()
        elif choice == "3":
            tid = ui.prompt("Enter Ticket ID")
            t = tm.search_by_id(tid)
            if t:
                ui.print_ticket_card(t.to_dict())
            else:
                ui.error(f"No ticket found with ID: {tid}")
        elif choice == "4":
            name = ui.prompt("Employee name")
            results = tm.search_by_employee(name)
            if results:
                ui.info(f"Found {len(results)} ticket(s) for '{name}'")
                for t in results:
                    ui.print_ticket_card(t.to_dict())
            else:
                ui.error(f"No tickets found for employee: {name}")
        elif choice == "5":
            update_status_flow()
        elif choice == "6":
            tid = ui.prompt("Ticket ID to close")
            try:
                t = tm.close_ticket(tid)
                ui.success(f"Ticket {t.ticket_id} closed successfully.")
            except TicketNotFoundError as e:
                ui.error(str(e))
        elif choice == "7":
            delete_ticket_flow()
        elif choice == "8":
            filter_by_status_flow()
        elif choice == "0":
            break
        ui.pause()


def view_all_tickets():
    all_t = tm.sort_by_priority()
    if not all_t:
        ui.warn("No tickets in the system yet.")
        return
    ui.info(f"Showing {len(all_t)} ticket(s) sorted by priority")
    for t in all_t:
        ui.print_ticket_card(t.to_dict())


def create_ticket_flow():
    os.system("cls" if os.name == "nt" else "clear")
    w = ui._w()
    ui.box_top("CREATE NEW TICKET", w, ui.BGREEN)
    ui.box_row("", w, ui.BGREEN)

    # Type selection
    ui.box_row(ui.c("  Select Ticket Type:", ui.BOLD, ui.BWHITE), w, ui.BGREEN)
    for k, (ttype, desc) in TICKET_TYPES.items():
        ui.box_row(f"    {ui.c(f'[{k}]', ui.BYELLOW)}  {ttype:<16} {ui.c(desc, ui.DIM)}", w, ui.BGREEN)
    ui.box_bot(w, ui.BGREEN)

    ttype_key  = ui.prompt("Type (1-4, default 1)")
    ticket_type, _ = TICKET_TYPES.get(ttype_key, TICKET_TYPES["1"])

    try:
        emp  = validate_non_empty(ui.prompt("Employee Name"), "Employee Name")
        dept = validate_non_empty(ui.prompt("Department"), "Department")

        # Category picker
        print()
        print(ui.c("  Issue Categories:", ui.BOLD, ui.BWHITE))
        for i, cat in enumerate(CATEGORIES, 1):
            print(f"    {ui.c(f'{i:2}.', ui.BYELLOW)} {cat}")
        cat_input = ui.prompt("Select number or type custom category")
        try:
            cat = CATEGORIES[int(cat_input) - 1]
        except (ValueError, IndexError):
            cat = cat_input or "Other"

        desc  = validate_non_empty(ui.prompt("Issue Description"), "Description")
        p_in  = ui.prompt("Priority (P1/P2/P3/P4) — leave blank to auto-detect")
        prio  = p_in.upper() if p_in.upper() in ("P1","P2","P3","P4") else None

        ticket = tm.create_ticket(
            employee_name=emp,
            department=dept,
            description=desc,
            category=cat,
            priority=prio,
            ticket_type=ticket_type,
        )
        print()
        ui.print_ticket_card(ticket.to_dict())
        ui.success(f"Ticket {ticket.ticket_id} created!  SLA: {ticket.get_sla_hours(ticket.priority)} hour(s)")

    except InvalidInputError as e:
        ui.error(f"Validation error: {e}")
    except Exception as e:
        ui.error(f"Unexpected error: {e}")
        system_logger.error(f"create_ticket_flow: {e}")


def update_status_flow():
    tid = ui.prompt("Ticket ID to update")
    t = tm.search_by_id(tid)
    if not t:
        ui.error(f"Ticket '{tid}' not found.")
        return
    ui.print_ticket_card(t.to_dict())
    print(ui.c("  Available statuses: ", ui.DIM) + ui.c(", ".join(sorted(VALID_STATUSES)), ui.BYELLOW))
    new_status = ui.prompt("New status")
    try:
        tm.update_status(tid, new_status)
        ui.success(f"Ticket {tid} status updated to '{new_status.title()}'.")
    except (TicketNotFoundError, InvalidInputError) as e:
        ui.error(str(e))


def delete_ticket_flow():
    tid = ui.prompt("Ticket ID to delete")
    t = tm.search_by_id(tid)
    if not t:
        ui.error(f"Ticket '{tid}' not found.")
        return
    ui.print_ticket_card(t.to_dict())
    confirm = ui.prompt(ui.c("Type 'DELETE' to confirm deletion", ui.BRED))
    if confirm == "DELETE":
        try:
            tm.delete_ticket(tid)
            ui.success(f"Ticket {tid} permanently deleted.")
        except TicketNotFoundError as e:
            ui.error(str(e))
    else:
        ui.info("Deletion cancelled.")


def filter_by_status_flow():
    print(ui.c("\n  Statuses: ", ui.DIM) + ui.c(", ".join(sorted(VALID_STATUSES)), ui.BYELLOW))
    status = ui.prompt("Filter by status").title()
    results = tm.search_by_status(status)
    if results:
        ui.info(f"Found {len(results)} ticket(s) with status '{status}'")
        for t in results:
            ui.print_ticket_card(t.to_dict())
    else:
        ui.warn(f"No tickets with status '{status}'.")


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM MONITOR
# ══════════════════════════════════════════════════════════════════════════════
def monitor_menu():
    while True:
        choice = ui.print_menu("SYSTEM MONITOR", [
            ("1", "View Current System Stats"),
            ("2", "Check Thresholds & Auto-Alert"),
            ("3", "Start Background Monitoring (30s)"),
            ("4", "Stop Background Monitoring"),
            ("0", "Back"),
        ], color=ui.BGREEN)

        if choice == "1":
            display_monitor_stats()
        elif choice == "2":
            check_alerts()
        elif choice == "3":
            monitor.start_background_monitoring(30)
            ui.success("Background monitoring started (every 30 seconds).")
        elif choice == "4":
            monitor.stop_background_monitoring()
            ui.info("Background monitoring stopped.")
        elif choice == "0":
            break
        ui.pause()


def display_monitor_stats():
    stats = monitor.get_current_stats()
    w = ui._w()

    def bar(val, max_val=100, width=30, warn=75, crit=90):
        pct   = min(val / max_val, 1.0)
        filled= int(pct * width)
        color = ui.BRED if val >= crit else ui.BYELLOW if val >= warn else ui.BGREEN
        return ui.c("█" * filled, color) + ui.c("░" * (width - filled), ui.DIM)

    ui.box_top("SYSTEM MONITOR — LIVE", w, ui.BGREEN)
    ui.box_row(ui.c(f"  {stats.timestamp}", ui.DIM), w, ui.BGREEN)
    ui.box_sep(w, ui.BGREEN)
    ui.box_row(f"  {ui.c('CPU     ', ui.BOLD)}  {bar(stats.cpu_percent)}  {ui.c(f'{stats.cpu_percent:5.1f}%', ui.BOLD, ui.BWHITE)}", w, ui.BGREEN)
    ui.box_row(f"  {ui.c('RAM     ', ui.BOLD)}  {bar(stats.ram_percent)}  {ui.c(f'{stats.ram_percent:5.1f}%', ui.BOLD, ui.BWHITE)}"
               + ui.c(f"  ({stats.ram_used_gb}/{stats.ram_total_gb} GB)", ui.DIM), w, ui.BGREEN)
    ui.box_row(f"  {ui.c('Disk    ', ui.BOLD)}  {bar(stats.disk_percent)}  {ui.c(f'{stats.disk_percent:5.1f}%', ui.BOLD, ui.BWHITE)}"
               + ui.c(f"  ({stats.disk_free_gb} GB free)", ui.DIM), w, ui.BGREEN)
    ui.box_sep(w, ui.BGREEN)
    ui.box_row(f"  {ui.c('Network ', ui.BOLD)}  {ui.c(f'Upload: {stats.net_sent_mb} MB', ui.BCYAN)}   {ui.c(f'Download: {stats.net_recv_mb} MB', ui.BYELLOW)}", w, ui.BGREEN)
    ui.box_bot(w, ui.BGREEN)
    print()


def check_alerts():
    alerts = monitor.check_and_alert()
    if alerts:
        ui.warn(f"{len(alerts)} alert(s) detected — P1 tickets auto-created!")
        for resource, msg in alerts:
            print(f"    {ui.c(f'[{resource}]', ui.BOLD, ui.BRED)}  {msg}")
    else:
        ui.success("All systems operating within normal thresholds.")


# ══════════════════════════════════════════════════════════════════════════════
# SLA MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
def sla_menu():
    while True:
        choice = ui.print_menu("SLA MANAGEMENT", [
            ("1", "View SLA Status — All Tickets"),
            ("2", "Check & Flag SLA Breaches"),
            ("3", "Escalate Breached Tickets"),
            ("0", "Back"),
        ], color=ui.BYELLOW)

        if choice == "1":
            display_sla_table()
        elif choice == "2":
            breached = sla.check_all_slas()
            if breached:
                ui.warn(f"{len(breached)} SLA breach(es) detected!")
                for t in breached:
                    print(f"    {ui.c(t['ticket_id'], ui.BCYAN)}  {ui.priority_color(t['priority'])}  {t['status']}")
            else:
                ui.success("No SLA breaches detected.")
        elif choice == "3":
            escalated = sla.escalate_breached()
            if escalated:
                ui.warn(f"Escalated {len(escalated)} ticket(s): {', '.join(escalated)}")
            else:
                ui.success("No tickets required escalation.")
        elif choice == "0":
            break
        ui.pause()


def display_sla_table():
    from utils import parse_dt, hours_since, SLA_HOURS
    tickets = tm.all_tickets()
    if not tickets:
        ui.warn("No tickets found.")
        return
    rows = []
    for t in sorted(tickets, key=lambda x: x.priority):
        elapsed = hours_since(t.created_at)
        limit   = SLA_HOURS.get(t.priority, 24)
        if t.status in ("Resolved", "Closed") and t.resolved_at:
            delta   = parse_dt(t.resolved_at) - parse_dt(t.created_at)
            elapsed = round(delta.total_seconds() / 3600, 1)
            met     = elapsed <= limit
            result  = ui.c(f"Met ({elapsed}h)", ui.BGREEN) if met else ui.c(f"Breached ({elapsed}h)", ui.BRED)
        else:
            remain  = round(limit - elapsed, 1)
            result  = ui.c(f"{remain}h left", ui.BGREEN) if remain > 0 else ui.c("BREACHED", ui.BRED)
        rows.append([
            t.ticket_id,
            ui.priority_color(t.priority),
            ui.status_color(t.status),
            f"{limit}h",
            result,
        ])
    print()
    ui.print_table(
        ["Ticket ID", "Priority", "Status", "SLA Limit", "SLA Result"],
        rows,
        col_colors=[ui.BCYAN, None, None, ui.DIM, None],
    )


# ══════════════════════════════════════════════════════════════════════════════
# PROBLEM MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
def problem_menu():
    while True:
        choice = ui.print_menu("PROBLEM MANAGEMENT  (ITIL)", [
            ("1", "Analyze Repeated Issues  (auto-raise if >= 5)"),
            ("2", "View All Problem Records"),
            ("0", "Back"),
        ], color=ui.BBLUE)

        if choice == "1":
            new_p = problem.analyze_repeated_issues()
            if new_p:
                ui.warn(f"{len(new_p)} new Problem Record(s) raised!")
                for p in new_p:
                    print(f"    {ui.c(p['problem_id'], ui.BCYAN)}  {ui.c(p['category'], ui.BYELLOW)}  x{p['occurrences']}")
            else:
                ui.success("No new problem records. (Need >= 5 occurrences per category)")
        elif choice == "2":
            display_problems()
        elif choice == "0":
            break
        ui.pause()


def display_problems():
    probs = problem._problems
    if not probs:
        ui.warn("No problem records found.")
        return
    rows = [[
        p.get("problem_id",""),
        p.get("category",""),
        str(p.get("occurrences",0)),
        p.get("status",""),
        p.get("detected_at","")[:16],
    ] for p in probs]
    print()
    ui.print_table(
        ["Problem ID", "Category", "Occurrences", "Status", "Detected"],
        rows,
        col_colors=[ui.BCYAN, ui.BYELLOW, ui.BRED, ui.BGREEN, ui.DIM],
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
def change_menu():
    while True:
        choice = ui.print_menu("CHANGE MANAGEMENT  (ITIL)", [
            ("1", "Raise Change Request"),
            ("2", "View All Change Requests"),
            ("0", "Back"),
        ], color=ui.BMAGENTA)

        if choice == "1":
            try:
                emp   = validate_non_empty(ui.prompt("Employee Name"), "Employee Name")
                dept  = validate_non_empty(ui.prompt("Department"), "Department")
                desc  = validate_non_empty(ui.prompt("Description of Change"), "Description")
                print(ui.c("  Change Types: Normal | Emergency | Standard", ui.DIM))
                ctype = ui.prompt("Change Type (default: Normal)").title()
                ctype = ctype if ctype in ("Normal","Emergency","Standard") else "Normal"
                t = change.raise_change_request(emp, dept, desc, ctype)
                ui.print_ticket_card(t.to_dict())
                ui.success(f"Change Request {t.ticket_id} raised [{ctype}].")
            except InvalidInputError as e:
                ui.error(str(e))
        elif choice == "2":
            display_changes()
        elif choice == "0":
            break
        ui.pause()


def display_changes():
    changes = [t for t in tm.all_tickets() if t.ticket_type == "Change"]
    if not changes:
        ui.warn("No change requests found.")
        return
    rows = [[
        t.ticket_id,
        getattr(t, "change_type", "Normal"),
        ui.status_color(t.status),
        t.employee_name,
        t.created_at[:16],
    ] for t in changes]
    print()
    ui.print_table(
        ["Ticket ID", "Change Type", "Status", "Raised By", "Created"],
        rows,
        col_colors=[ui.BCYAN, ui.BYELLOW, None, ui.BWHITE, ui.DIM],
    )


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════════════════
def reports_menu():
    while True:
        choice = ui.print_menu("REPORTS", [
            ("1", "Daily Report  — Today"),
            ("2", "Monthly Report — This Month"),
            ("3", "Daily Report  — Custom Date"),
            ("4", "Monthly Report — Custom Month"),
            ("0", "Back"),
        ], color=ui.BMAGENTA)

        if choice == "1":
            rpt.generate_daily_report()
        elif choice == "2":
            rpt.generate_monthly_report()
        elif choice == "3":
            date_str = ui.prompt("Date (YYYY-MM-DD)")
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                rpt.generate_daily_report(dt)
            except ValueError:
                ui.error("Invalid date format. Use YYYY-MM-DD.")
        elif choice == "4":
            ym = ui.prompt("Year-Month (YYYY-MM)")
            try:
                dt = datetime.strptime(ym, "%Y-%m")
                rpt.generate_monthly_report(dt.year, dt.month)
            except ValueError:
                ui.error("Invalid format. Use YYYY-MM.")
        elif choice == "0":
            break
        ui.pause()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    system_logger.info("Smart IT Service Desk started.")
    while True:
        choice = main_menu()

        if choice == "1":
            ticket_menu()
        elif choice == "2":
            monitor_menu()
        elif choice == "3":
            sla_menu()
        elif choice == "4":
            problem_menu()
        elif choice == "5":
            change_menu()
        elif choice == "6":
            reports_menu()
        elif choice == "7":
            try:
                tm.backup_to_csv()
                ui.success("Backup complete. See data/backup.csv")
            except Exception as e:
                ui.error(f"Backup failed: {e}")
            ui.pause()
        elif choice == "0":
            os.system("cls" if os.name == "nt" else "clear")
            print(ui.c("\n  Goodbye! Smart IT Service Desk shutting down.\n", ui.BCYAN))
            system_logger.info("Smart IT Service Desk exited.")
            sys.exit(0)
        else:
            ui.error("Invalid option. Please try again.")
            ui.pause()


if __name__ == "__main__":
    main()
