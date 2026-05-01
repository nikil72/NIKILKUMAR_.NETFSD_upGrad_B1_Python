"""
monitor.py - System Monitoring Module for Smart IT Service Desk
Monitors CPU, Memory, Disk, and Network; auto-creates P1 tickets on breach.
"""

import psutil
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from logger import monitor_logger, log_action
from utils import now_str, print_separator


# ── Thresholds ─────────────────────────────────────────────────────────────────
CPU_THRESHOLD    = 90.0   # %
RAM_THRESHOLD    = 95.0   # %
DISK_THRESHOLD   = 90.0   # % used  (free < 10%)
MONITOR_INTERVAL = 30     # seconds between checks


class SystemStats:
    """Snapshot of system resource usage."""

    def __init__(self):
        self.timestamp   = now_str()
        self.cpu_percent = psutil.cpu_percent(interval=1)
        vm               = psutil.virtual_memory()
        self.ram_percent = vm.percent
        self.ram_used_gb = round(vm.used / (1024 ** 3), 2)
        self.ram_total_gb = round(vm.total / (1024 ** 3), 2)
        du               = psutil.disk_usage("/")
        self.disk_percent = du.percent
        self.disk_free_gb = round(du.free / (1024 ** 3), 2)
        self.disk_total_gb = round(du.total / (1024 ** 3), 2)
        try:
            net = psutil.net_io_counters()
            self.net_sent_mb = round(net.bytes_sent / (1024 ** 2), 2)
            self.net_recv_mb = round(net.bytes_recv / (1024 ** 2), 2)
        except Exception:
            self.net_sent_mb = 0.0
            self.net_recv_mb = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp":    self.timestamp,
            "cpu_percent":  self.cpu_percent,
            "ram_percent":  self.ram_percent,
            "ram_used_gb":  self.ram_used_gb,
            "ram_total_gb": self.ram_total_gb,
            "disk_percent": self.disk_percent,
            "disk_free_gb": self.disk_free_gb,
            "disk_total_gb": self.disk_total_gb,
            "net_sent_mb":  self.net_sent_mb,
            "net_recv_mb":  self.net_recv_mb,
        }

    def __str__(self) -> str:
        return (
            f"[{self.timestamp}] "
            f"CPU: {self.cpu_percent}% | "
            f"RAM: {self.ram_percent}% ({self.ram_used_gb}/{self.ram_total_gb} GB) | "
            f"Disk: {self.disk_percent}% (Free: {self.disk_free_gb} GB) | "
            f"Net ↑{self.net_sent_mb} MB ↓{self.net_recv_mb} MB"
        )


class Monitor:
    """
    System monitor that polls resource usage and auto-creates tickets
    when thresholds are breached.
    """

    def __init__(self, ticket_manager=None):
        self._ticket_manager = ticket_manager
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_stats: Optional[SystemStats] = None
        self._alert_cooldown: Dict[str, str] = {}   # resource → last alert time

    # ── Public API ─────────────────────────────────────────────────────────────
    @log_action(monitor_logger)
    def get_current_stats(self) -> SystemStats:
        stats = SystemStats()
        self._last_stats = stats
        monitor_logger.info(str(stats))
        return stats

    def display_stats(self):
        stats = self.get_current_stats()
        print_separator()
        print("  📊  SYSTEM MONITOR")
        print_separator()
        print(f"  🕐 Time      : {stats.timestamp}")
        print(f"  🖥️  CPU       : {stats.cpu_percent}%"
              + ("  ⚠️  HIGH" if stats.cpu_percent >= CPU_THRESHOLD else ""))
        print(f"  💾 RAM       : {stats.ram_percent}% "
              f"({stats.ram_used_gb} / {stats.ram_total_gb} GB)"
              + ("  ⚠️  HIGH" if stats.ram_percent >= RAM_THRESHOLD else ""))
        print(f"  💿 Disk      : {stats.disk_percent}% used "
              f"(Free: {stats.disk_free_gb} GB)"
              + ("  ⚠️  LOW" if stats.disk_percent >= DISK_THRESHOLD else ""))
        print(f"  🌐 Network   : ↑ {stats.net_sent_mb} MB  ↓ {stats.net_recv_mb} MB")
        print_separator()

    def check_and_alert(self) -> list:
        """Check thresholds and auto-create tickets if breached. Returns list of alerts."""
        stats  = self.get_current_stats()
        alerts = []

        if stats.cpu_percent >= CPU_THRESHOLD:
            msg = f"High CPU usage detected: {stats.cpu_percent}%"
            alerts.append(("CPU", msg))
            monitor_logger.critical(msg)
            self._auto_create_ticket("CPU", msg)

        if stats.ram_percent >= RAM_THRESHOLD:
            msg = f"High RAM usage detected: {stats.ram_percent}%"
            alerts.append(("RAM", msg))
            monitor_logger.critical(msg)
            self._auto_create_ticket("RAM", msg)

        if stats.disk_percent >= DISK_THRESHOLD:
            msg = f"Low disk space: only {stats.disk_free_gb} GB free ({stats.disk_percent}% used)"
            alerts.append(("DISK", msg))
            monitor_logger.critical(msg)
            self._auto_create_ticket("DISK", msg)

        if not alerts:
            monitor_logger.info("All system resources within normal limits.")

        return alerts

    # ── Background Monitoring ─────────────────────────────────────────────────
    def start_background_monitoring(self, interval: int = MONITOR_INTERVAL):
        if self._running:
            monitor_logger.warning("Monitor already running.")
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, args=(interval,), daemon=True
        )
        self._thread.start()
        monitor_logger.info(f"Background monitoring started (interval={interval}s)")

    def stop_background_monitoring(self):
        self._running = False
        monitor_logger.info("Background monitoring stopped.")

    def _monitor_loop(self, interval: int):
        while self._running:
            try:
                self.check_and_alert()
            except Exception as e:
                monitor_logger.error(f"Monitor loop error: {e}")
            time.sleep(interval)

    # ── Auto-ticket Creation ──────────────────────────────────────────────────
    def _auto_create_ticket(self, resource: str, description: str):
        if self._ticket_manager is None:
            return
        # Cooldown: avoid spam-creating tickets for the same resource
        last = self._alert_cooldown.get(resource)
        if last:
            from utils import hours_since
            if hours_since(last) < 1:
                monitor_logger.warning(f"Alert cooldown active for {resource} – skipping ticket.")
                return

        try:
            ticket = self._ticket_manager.create_ticket(
                employee_name="System Monitor",
                department="IT Infrastructure",
                description=description,
                category=f"{resource} Alert",
                priority="P1",
                ticket_type="Incident",
            )
            self._alert_cooldown[resource] = now_str()
            monitor_logger.info(f"Auto-ticket created: {ticket.ticket_id} for {resource}")
        except Exception as e:
            monitor_logger.error(f"Failed to auto-create ticket for {resource}: {e}")
