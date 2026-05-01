
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
=======
# ⚡ ELearn Platform — Full-Stack ASP.NET Core 8 + SQLite

A complete multi-layered e-learning web application with MVC views, REST APIs, and **Swagger UI**.

---

## 🚀 Quick Start

### Prerequisites
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- VS Code with C# Dev Kit extension (optional)

### Run the Project

```bash
# 1. Navigate to project folder
cd B5_.Net Standard_Nikil Kumar_MultiPage_E-Learning_Platform_Backend

# 2. IMPORTANT: Fix Result<> generics (see note below)
#    In VS Code: Ctrl+Shift+H (Find & Replace in all files)
#    Find:    <r>           Replace: <Result>
#    Find:    new List<r>() Replace: new List<Result>()
#    Find:    new r {       Replace: new Result {
#    Find:    Task<r>       Replace: Task<Result>
#    Find:    IEnumerable<r> Replace: IEnumerable<Result>
#    Find:    Set<r>()      Replace: Set<Result>()
#    Find:    DbSet<r>      Replace: DbSet<Result>
#    Find:    Entity<r>()   Replace: Entity<Result>()

# 3. Restore packages
dotnet restore

# 4. Run (SQLite DB auto-created + seeded)
dotnet run
```

### URLs
| Page | URL |
|------|-----|
| 🏠 Dashboard | http://localhost:5000 |
| 📚 Courses | http://localhost:5000/Courses |
| 🔌 **Swagger UI** | **http://localhost:5000/swagger** |
| 👤 Profile | http://localhost:5000/Profile |

---

## 🔑 Default Login
| Email | Password |
|-------|----------|
| admin@elearn.com | Admin@123 |

---

## 🔌 REST API Endpoints

### Courses
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/courses | All courses |
| GET | /api/courses/{id} | Single course |
| POST | /api/courses | Create course |
| PUT | /api/courses/{id} | Update course |
| DELETE | /api/courses/{id} | Delete course |

### Lessons
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/courses/{courseId}/lessons | Course lessons |
| POST | /api/lessons | Create lesson |
| PUT | /api/lessons/{id} | Update lesson |
| DELETE | /api/lessons/{id} | Delete lesson |

### Quizzes
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/quizzes/{courseId} | Course quizzes |
| POST | /api/quizzes | Create quiz |
| GET | /api/quizzes/{quizId}/questions | Quiz questions |
| POST | /api/questions | Add question |
| POST | /api/quizzes/{quizId}/submit | Submit answers |
| GET | /api/results/{userId} | User results |

### Users
| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/users/register | Register |
| GET | /api/users/{id} | Get user |
| PUT | /api/users/{id} | Update user |

---

## 🏗️ Architecture

```
B5_.Net Standard_Nikil Kumar_MultiPage_E-Learning_Platform_Backend/
├── Controllers/
│   ├── API/                  ← REST API Controllers (Swagger documented)
│   │   ├── CoursesApiController.cs
│   │   ├── LessonsApiController.cs
│   │   ├── QuizzesApiController.cs
│   │   └── UsersApiController.cs
│   ├── HomeController.cs     ← Login / Register / Dashboard
│   ├── CoursesController.cs  ← MVC Course pages
│   ├── QuizzesController.cs  ← Quiz take + submit
│   └── ProfileController.cs  ← User profile + history
├── Models/
│   ├── Entities/             ← EF Core entity classes
│   └── DTOs/                 ← Data Transfer Objects (no entity exposure)
├── Data/
│   ├── AppDbContext.cs       ← EF Core DbContext (Fluent API)
│   └── DbSeeder.cs           ← Seed data
├── Repositories/             ← Repository pattern
├── Services/                 ← Business logic layer
├── Mappings/                 ← AutoMapper profiles
├── Views/                    ← Razor MVC views (dark UI)
├── wwwroot/
│   ├── css/site.css          ← Dark theme
│   └── css/swagger-custom.css ← Custom Swagger dark theme
├── Tests/ELearnTests.cs      ← xUnit unit tests
└── SQL_Queries.sql           ← SQL reference (SELECT/JOIN/GROUP/UNION/DML)
```

---

## ✅ Features Checklist

- [x] SQLite database (6 tables, all relationships)
- [x] EF Core 8 with Fluent API + Eager Loading + AsNoTracking
- [x] Repository Pattern (6 repositories)
- [x] Service Layer (5 services)
- [x] AutoMapper (DTOs, no entity exposure)
- [x] BCrypt password hashing
- [x] **Swagger UI** with dark theme + XML documentation
- [x] All REST APIs (Courses/Lessons/Quizzes/Users/Results)
- [x] Proper HTTP status codes (200/201/400/404/204)
- [x] Input validation (ModelState + DataAnnotations)
- [x] MVC Views (Dashboard, Courses, Quiz, Profile)
- [x] Session-based authentication
- [x] Quiz timer + real-time progress bar
- [x] SQL queries (SELECT/WHERE/JOIN/GROUP BY/UNION/DML)
- [x] Unit tests (7 tests)
- [x] Responsive dark UI

---

## 🧪 Running Tests

```bash
# From project root
dotnet test Tests/ELearnTests.cs
# Or add as separate test project and run:
dotnet test
```
>>>>>>> 1f513a7b1c61f9a212bae79db0cead50878c6f7c
