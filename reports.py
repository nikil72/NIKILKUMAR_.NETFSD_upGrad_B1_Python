"""
reports.py - Report Generator for Smart IT Service Desk
Generates daily and monthly reports with rich terminal output.
"""

import os
import json
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any
from functools import reduce

from utils import (
    hours_since, SLA_HOURS, now_str, parse_dt,
    filter_by_status, count_total_priority, print_separator
)
from logger import report_logger, log_action

DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")


class ReportGenerator:
    """Generates daily and monthly reports from ticket data."""

    def __init__(self, ticket_manager):
        self._tm = ticket_manager
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def _all_dicts(self) -> List[Dict]:
        return [t.to_dict() for t in self._tm.all_tickets()]

    def _tickets_in_range(self, start: datetime, end: datetime) -> List[Dict]:
        result = []
        for t in self._all_dicts():
            try:
                created = parse_dt(t["created_at"])
                if start <= created <= end:
                    result.append(t)
            except Exception:
                pass
        return result

    @staticmethod
    def _avg_resolution_hours(tickets: List[Dict]) -> float:
        resolved = [t for t in tickets if t.get("resolved_at") and t.get("created_at")]
        if not resolved:
            return 0.0
        total = reduce(
            lambda acc, t: acc + (
                (parse_dt(t["resolved_at"]) - parse_dt(t["created_at"])).total_seconds() / 3600
            ),
            resolved, 0.0,
        )
        return round(total / len(resolved), 2)

    @log_action(report_logger)
    def generate_daily_report(self, target_date: datetime = None) -> Dict:
        target_date = target_date or datetime.now()
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end   = target_date.replace(hour=23, minute=59, second=59)

        tickets    = self._tickets_in_range(start, end)
        open_t     = filter_by_status(tickets, "Open")
        closed_t   = filter_by_status(tickets, "Closed")
        resolved_t = filter_by_status(tickets, "Resolved")
        high_prio  = [t for t in tickets if t["priority"] in ("P1", "P2")]
        breached   = [t for t in tickets if t.get("sla_breached")]

        report = {
            "report_type":           "Daily",
            "date":                  target_date.strftime("%Y-%m-%d"),
            "generated_at":          now_str(),
            "total_tickets":         len(tickets),
            "open_tickets":          len(open_t),
            "closed_tickets":        len(closed_t) + len(resolved_t),
            "high_priority_tickets": len(high_prio),
            "sla_breaches":          len(breached),
            "p1_count":              count_total_priority(tickets, "P1"),
            "p2_count":              count_total_priority(tickets, "P2"),
            "p3_count":              count_total_priority(tickets, "P3"),
            "p4_count":              count_total_priority(tickets, "P4"),
            "avg_resolution_hours":  self._avg_resolution_hours(tickets),
            "tickets":               tickets,
        }

        self._save_report(report, f"daily_{target_date.strftime('%Y-%m-%d')}.json")
        self._print_daily(report)
        return report

    def _print_daily(self, r: Dict):
        from ui import (
            box_top, box_bot, box_row, box_sep,
            print_stat_row, print_bar_chart, print_table,
            priority_color, status_color,
            c, BOLD, BWHITE, DIM, BCYAN, BYELLOW, BRED, BGREEN,
            CYAN, thin_sep, _w
        )
        w = _w()
        box_top(f"DAILY REPORT  ·  {r['date']}", w, CYAN)
        box_row(c(f"  Generated: {r['generated_at']}", DIM), w, CYAN)
        box_bot(w, CYAN)
        print()

        print_stat_row([
            ("Total Tickets",   r["total_tickets"],         BWHITE),
            ("Open",            r["open_tickets"],          BGREEN),
            ("Closed/Resolved", r["closed_tickets"],        BCYAN),
            ("High Priority",   r["high_priority_tickets"], BRED),
            ("SLA Breaches",    r["sla_breaches"],          BYELLOW),
        ])

        prio_data = [
            ("P1 - Critical", r["p1_count"]),
            ("P2 - High",     r["p2_count"]),
            ("P3 - Medium",   r["p3_count"]),
            ("P4 - Low",      r["p4_count"]),
        ]
        print_bar_chart("Priority Breakdown", prio_data, color=BCYAN)

        avg = r["avg_resolution_hours"]
        avg_str = f"{avg} hrs" if avg else "N/A (no resolved tickets yet)"
        print(f"  {c('Avg Resolution Time:', DIM)}  {c(avg_str, BOLD, BYELLOW)}\n")

        tickets = r.get("tickets", [])
        if tickets:
            print(c("  Ticket List", BOLD, BWHITE))
            thin_sep(w)
            rows = []
            for t in sorted(tickets, key=lambda x: x.get("priority", "P4")):
                rows.append([
                    t.get("ticket_id", ""),
                    priority_color(t.get("priority", "")),
                    status_color(t.get("status", "")),
                    t.get("employee_name", "")[:18],
                    t.get("category", "")[:22],
                    t.get("created_at", "")[:16],
                ])
            print_table(
                ["Ticket ID", "Priority", "Status", "Employee", "Category", "Created"],
                rows,
                col_colors=[BCYAN, None, None, BWHITE, BYELLOW, DIM],
            )
        else:
            print(c("  No tickets created on this date.\n", DIM))

        print(c(f"  Report saved to: data/reports/daily_{r['date']}.json", DIM))
        print()

    @log_action(report_logger)
    def generate_monthly_report(self, year: int = None, month: int = None) -> Dict:
        now   = datetime.now()
        year  = year  or now.year
        month = month or now.month
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        tickets         = self._tickets_in_range(start, end)
        category_counts = Counter(t["category"] for t in tickets)
        dept_counts     = Counter(t["department"] for t in tickets)
        most_common_cat  = category_counts.most_common(1)
        most_common_dept = dept_counts.most_common(1)
        problem_cats     = [cat for cat, cnt in category_counts.items() if cnt >= 5]

        week_counts = Counter()
        for t in tickets:
            try:
                wk = parse_dt(t["created_at"]).isocalendar()[1]
                week_counts[f"Week {wk}"] += 1
            except Exception:
                pass

        prio_res = {}
        for p in ("P1", "P2", "P3", "P4"):
            subset = [t for t in tickets if t.get("priority") == p]
            prio_res[p] = self._avg_resolution_hours(subset)

        report = {
            "report_type":             "Monthly",
            "year":                    year,
            "month":                   month,
            "generated_at":            now_str(),
            "total_tickets":           len(tickets),
            "most_common_issue":       most_common_cat[0][0]  if most_common_cat  else "N/A",
            "most_common_issue_count": most_common_cat[0][1]  if most_common_cat  else 0,
            "avg_resolution_hours":    self._avg_resolution_hours(tickets),
            "dept_most_incidents":     most_common_dept[0][0] if most_common_dept else "N/A",
            "repeated_problems":       problem_cats,
            "sla_breaches":            len([t for t in tickets if t.get("sla_breached")]),
            "category_breakdown":      dict(category_counts),
            "department_breakdown":    dict(dept_counts),
            "week_counts":             dict(week_counts),
            "priority_avg_resolution": prio_res,
        }

        self._save_report(report, f"monthly_{year}_{month:02d}.json")
        self._print_monthly(report)
        return report

    def _print_monthly(self, r: Dict):
        from ui import (
            box_top, box_bot, box_row, box_sep,
            print_stat_row, print_bar_chart, print_table,
            priority_color, status_color,
            c, BOLD, BWHITE, DIM, BCYAN, BYELLOW, BRED, BGREEN, BBLUE,
            BMAGENTA, thin_sep, _w
        )
        import calendar
        month_name = calendar.month_name[r["month"]]
        w = _w()

        box_top(f"MONTHLY REPORT  ·  {month_name} {r['year']}", w, BMAGENTA)
        box_row(c(f"  Generated: {r['generated_at']}", DIM), w, BMAGENTA)
        box_bot(w, BMAGENTA)
        print()

        print_stat_row([
            ("Total Tickets",   r["total_tickets"],               BWHITE),
            ("SLA Breaches",    r["sla_breaches"],                BRED),
            ("Top Issue Count", r["most_common_issue_count"],     BYELLOW),
            ("Avg Resolution",  f"{r['avg_resolution_hours']}h", BCYAN),
        ])

        cnt_str = f"({r['most_common_issue_count']} tickets)"
        print(f"  {c('Most Common Issue  :', DIM)}  {c(r['most_common_issue'], BOLD, BYELLOW)}  {c(cnt_str, DIM)}")
        print(f"  {c('Top Department     :', DIM)}  {c(r['dept_most_incidents'], BOLD, BGREEN)}")
        if r["repeated_problems"]:
            print(f"  {c('Repeated Problems  :', DIM)}  {c(', '.join(r['repeated_problems']), BOLD, BRED)}")
        print()

        cat_data = sorted(r["category_breakdown"].items(), key=lambda x: -x[1])[:10]
        print_bar_chart("Top Issue Categories", cat_data, color=BCYAN)

        dept_data = sorted(r["department_breakdown"].items(), key=lambda x: -x[1])
        print_bar_chart("Incidents by Department", dept_data, color=BBLUE)

        week_data = sorted(r.get("week_counts", {}).items())
        if week_data:
            print_bar_chart("Weekly Ticket Volume", week_data, color=BMAGENTA, bar_char="▓")

        prio_res = r.get("priority_avg_resolution", {})
        if any(v > 0 for v in prio_res.values()):
            print(c("  Avg Resolution Time by Priority", BOLD, BWHITE))
            thin_sep(w)
            rows = []
            for p in ("P1", "P2", "P3", "P4"):
                hrs = prio_res.get(p, 0.0)
                sla = {"P1": 1, "P2": 4, "P3": 8, "P4": 24}.get(p, 24)
                result = c("Within SLA", BGREEN) if (hrs > 0 and hrs <= sla) else \
                         c("Breached",   BRED)   if hrs > 0 else c("No data", DIM)
                rows.append([priority_color(p), f"{hrs}h", f"{sla}h", result])
            print_table(
                ["Priority", "Avg Time", "SLA Limit", "Result"],
                rows,
                col_colors=[None, BYELLOW, DIM, None],
            )

        if r["category_breakdown"]:
            print(c("  Full Category Breakdown", BOLD, BWHITE))
            thin_sep(w)
            cat_rows = [
                [cat[:30], str(cnt),
                 c("Recurring (5+)", BRED) if cnt >= 5 else c("Normal", DIM)]
                for cat, cnt in sorted(r["category_breakdown"].items(), key=lambda x: -x[1])
            ]
            print_table(["Category", "Count", "Note"], cat_rows,
                        col_colors=[BYELLOW, BWHITE, None])

        print(c(f"  Report saved to: data/reports/monthly_{r['year']}_{r['month']:02d}.json", DIM))
        print()

    def _save_report(self, report: Dict, filename: str):
        save_data = {k: v for k, v in report.items() if k != "tickets"}
        path = os.path.join(REPORTS_DIR, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            report_logger.info(f"Report saved to {path}")
        except OSError as e:
            report_logger.error(f"Failed to save report: {e}")
