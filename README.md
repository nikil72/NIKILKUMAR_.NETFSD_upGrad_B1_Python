# 🖥️ Smart IT Service Desk — Automation System

A complete Python-based IT helpdesk automation system implementing
**ITIL workflows**, **OOP**, **System Monitoring**, **SLA Tracking**,
**Logging**, and **Reports**.

---

## 📁 Project Structure

```
smart_it_service_desk/
├── main.py           # Interactive CLI entry point
├── tickets.py        # OOP Ticket classes + TicketManager
├── monitor.py        # System monitoring (CPU/RAM/Disk/Network)
├── reports.py        # Daily & Monthly report generator
├── itil.py           # ITIL: SLA, Problem, Change management
├── utils.py          # Shared utilities, custom exceptions, helpers
├── logger.py         # Centralised logging module
├── test_suite.py     # 35+ unit test cases
├── requirements.txt
├── README.md
└── data/
    ├── tickets.json  # Persistent ticket store
    ├── logs.txt      # Application log file
    ├── backup.csv    # CSV backup of all tickets
    ├── problems.json # Problem records
    └── reports/      # Generated report JSON files
```

---

## ⚡ Quick Start

### 1. Clone / Download the project

```bash
git clone <your-repo-url>
cd smart_it_service_desk
```

### 2. Create a Virtual Environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

### 5. Run Tests

```bash
python -m pytest test_suite.py -v
```

---

## 🧩 Features

### Ticket Management
- Create / View / Search / Update / Close / Delete tickets
- Ticket types: **Incident**, **Service Request**, **Problem Record**, **Change Request**
- Auto-priority detection from issue description keywords
- Priority rules: P1 (Server Down) → P4 (Password Reset)

### System Monitoring
- Real-time CPU, RAM, Disk, Network stats via `psutil`
- Auto-creates **P1 Incident ticket** when:
  - CPU > 90%
  - RAM > 95%
  - Disk used > 90%
- Optional background monitoring thread (30-second intervals)

### SLA Tracking

| Priority | SLA Limit |
|----------|-----------|
| P1       | 1 hour    |
| P2       | 4 hours   |
| P3       | 8 hours   |
| P4       | 24 hours  |

- Flags breached tickets with warnings
- Auto-escalates tickets exceeding SLA

### ITIL Workflows
- **Incident Management** — rapid response to outages
- **Service Request Management** — password reset, software installs
- **Problem Management** — auto-raises Problem Record if same category occurs ≥5 times
- **Change Management** — Normal / Emergency / Standard change requests
- **SLA Monitoring** — full lifecycle tracking

### Reports
- **Daily Report**: total, open, closed, high priority, SLA breaches
- **Monthly Report**: most common issue, avg resolution time, dept breakdown
- Reports auto-saved as JSON in `data/reports/`

### Logging
Uses Python `logging` module with levels: INFO, WARNING, ERROR, CRITICAL.
All events written to `data/logs.txt` and printed to console.

---

## 🐍 Python Concepts Covered

| Category | Concepts |
|----------|---------|
| Basics | Variables, Data Types, I/O, Conditions, Loops, Functions |
| OOP | Classes, Inheritance, Polymorphism, Encapsulation, Static/Class Methods, Dunder Methods |
| File Handling | JSON read/write, CSV backup, context managers |
| Exception Handling | try/except/finally, custom exceptions, raise |
| Advanced | Decorators, Generators, Iterators, map/filter/reduce, regex |

---

## 🗂️ Data Files

| File | Purpose |
|------|---------|
| `data/tickets.json` | All ticket records (auto-created) |
| `data/logs.txt` | Application event log |
| `data/backup.csv` | CSV backup (manual or auto) |
| `data/problems.json` | Problem records |
| `data/reports/*.json` | Generated reports |

---

## 🧪 Test Cases (35+)

| # | Test Group | What is Tested |
|---|-----------|---------------|
| 1 | Ticket Creation | All ticket types, validation, persistence |
| 2 | Priority Logic | Auto-detection, overrides, edge cases |
| 3 | SLA Breach | Breach detection for all priorities |
| 4 | Auto Monitoring | High CPU/RAM triggers P1 ticket |
| 5 | File Read/Write | JSON save/reload, CSV backup |
| 6 | Search Ticket | By ID, employee, status, sort |
| 7 | Exception Handling | All custom exceptions |
| 8 | Iterators/Generators | TicketIterator, open_ticket_generator |
| 9 | OOP/Inheritance | Class hierarchy, polymorphism, serialisation |

---

## 👨‍💻 Author

**Kunal** — Smart IT Service Desk Project  
Python | OOP | ITIL | System Automation
