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
