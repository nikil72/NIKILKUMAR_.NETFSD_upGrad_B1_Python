using ELearnPlatform.Models.Entities;

namespace ELearnPlatform.Data;

public static class DbSeeder
{
    public static void Seed(AppDbContext db)
    {
        if (db.Users.Any()) return;

        var admin = new User
        {
            FullName = "Admin User",
            Email = "admin@elearn.com",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin@123"),
            CreatedAt = DateTime.UtcNow
        };
        db.Users.Add(admin);
        db.SaveChanges();

        var courses = new List<Course>
        {
            new() { Title = "ASP.NET Core Masterclass", Description = "Build enterprise-grade web apps with ASP.NET Core 8, EF Core, and REST APIs.", Category = "Backend", CreatedBy = admin.UserId },
            new() { Title = "C# Deep Dive", Description = "Advanced C# concepts: LINQ, generics, async/await, and design patterns.", Category = "Programming", CreatedBy = admin.UserId },
            new() { Title = "SQL & SQLite Essentials", Description = "Master SQL queries, joins, aggregation, and performance tuning with SQLite.", Category = "Database", CreatedBy = admin.UserId },
            new() { Title = "Clean Architecture in .NET", Description = "Learn repository pattern, CQRS, and domain-driven design in .NET applications.", Category = "Architecture", CreatedBy = admin.UserId },
        };
        db.Courses.AddRange(courses);
        db.SaveChanges();

        var lessons = new List<Lesson>
        {
            new() { CourseId = courses[0].CourseId, Title = "Introduction to MVC", Content = "MVC separates application concerns into three layers: Model handles data, View handles UI, and Controller handles logic. This makes code maintainable and testable.", OrderIndex = 1 },
            new() { CourseId = courses[0].CourseId, Title = "Entity Framework Core Setup", Content = "EF Core is an ORM that maps C# classes to database tables. Configure DbContext, add DbSets, and use migrations to keep schema in sync.", OrderIndex = 2 },
            new() { CourseId = courses[0].CourseId, Title = "Building REST APIs", Content = "REST APIs expose data via HTTP verbs: GET retrieves, POST creates, PUT updates, DELETE removes. Use [ApiController] and [Route] attributes.", OrderIndex = 3 },
            new() { CourseId = courses[1].CourseId, Title = "LINQ Fundamentals", Content = "LINQ (Language Integrated Query) lets you query collections using C# syntax. Key operators: Where, Select, GroupBy, OrderBy, FirstOrDefault.", OrderIndex = 1 },
            new() { CourseId = courses[1].CourseId, Title = "Async/Await Patterns", Content = "async/await enables non-blocking operations. Always use async all the way down, use ConfigureAwait(false) in libraries, and handle exceptions with try/catch.", OrderIndex = 2 },
            new() { CourseId = courses[2].CourseId, Title = "SQL Joins Explained", Content = "INNER JOIN returns matching rows, LEFT JOIN returns all left rows + matches, RIGHT JOIN returns all right rows + matches, FULL OUTER JOIN returns all rows.", OrderIndex = 1 },
        };
        db.Lessons.AddRange(lessons);
        db.SaveChanges();

        var quiz1 = new Quiz { CourseId = courses[0].CourseId, Title = "ASP.NET Core Fundamentals Quiz" };
        var quiz2 = new Quiz { CourseId = courses[1].CourseId, Title = "C# Advanced Quiz" };
        var quiz3 = new Quiz { CourseId = courses[2].CourseId, Title = "SQL Mastery Quiz" };
        db.Quizzes.AddRange(quiz1, quiz2, quiz3);
        db.SaveChanges();

        var questions = new List<Question>
        {
            // Quiz 1
            new() { QuizId = quiz1.QuizId, QuestionText = "What does MVC stand for?", OptionA = "Model View Controller", OptionB = "Module View Component", OptionC = "Main View Core", OptionD = "Managed Visual Code", CorrectAnswer = "A" },
            new() { QuizId = quiz1.QuizId, QuestionText = "Which method saves EF Core changes to the database?", OptionA = "CommitAsync()", OptionB = "SaveChangesAsync()", OptionC = "UpdateAsync()", OptionD = "FlushAsync()", CorrectAnswer = "B" },
            new() { QuizId = quiz1.QuizId, QuestionText = "What HTTP verb is used to CREATE a resource?", OptionA = "GET", OptionB = "PUT", OptionC = "POST", OptionD = "DELETE", CorrectAnswer = "C" },
            new() { QuizId = quiz1.QuizId, QuestionText = "What does AsNoTracking() do in EF Core?", OptionA = "Deletes all tracked entities", OptionB = "Improves read performance by skipping change tracking", OptionC = "Tracks only new entities", OptionD = "Disables lazy loading", CorrectAnswer = "B" },
            new() { QuizId = quiz1.QuizId, QuestionText = "Which attribute marks a class as an API controller?", OptionA = "[Controller]", OptionB = "[MvcController]", OptionC = "[ApiController]", OptionD = "[HttpController]", CorrectAnswer = "C" },
            // Quiz 2
            new() { QuizId = quiz2.QuizId, QuestionText = "Which LINQ method filters a sequence?", OptionA = "Select()", OptionB = "Where()", OptionC = "GroupBy()", OptionD = "OrderBy()", CorrectAnswer = "B" },
            new() { QuizId = quiz2.QuizId, QuestionText = "What keyword is used to call an async method?", OptionA = "async", OptionB = "sync", OptionC = "await", OptionD = "task", CorrectAnswer = "C" },
            new() { QuizId = quiz2.QuizId, QuestionText = "What does the null-coalescing operator ?? do?", OptionA = "Throws if null", OptionB = "Returns left if not null, else right", OptionC = "Sets value to null", OptionD = "Compares two nulls", CorrectAnswer = "B" },
            // Quiz 3
            new() { QuizId = quiz3.QuizId, QuestionText = "Which JOIN returns only matching rows from both tables?", OptionA = "LEFT JOIN", OptionB = "RIGHT JOIN", OptionC = "FULL JOIN", OptionD = "INNER JOIN", CorrectAnswer = "D" },
            new() { QuizId = quiz3.QuizId, QuestionText = "Which SQL clause is used with aggregate functions?", OptionA = "WHERE", OptionB = "HAVING", OptionC = "ORDER BY", OptionD = "GROUP BY", CorrectAnswer = "D" },
            new() { QuizId = quiz3.QuizId, QuestionText = "What does COUNT(*) return?", OptionA = "Sum of all values", OptionB = "Number of non-null values", OptionC = "Total number of rows", OptionD = "Average of values", CorrectAnswer = "C" },
        };
        db.Questions.AddRange(questions);
        db.SaveChanges();
    }
}
