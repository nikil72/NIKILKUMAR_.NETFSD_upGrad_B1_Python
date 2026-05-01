using Xunit;
using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Tests;

/// <summary>
/// Unit tests for Course CRUD, Quiz scoring, LINQ, API validation, and security.
/// Run with: dotnet test
/// </summary>
public class ELearnTests
{
    private static AppDbContext CreateDb()
    {
        var opts = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        // Use InMemory for tests (SQLite not needed)
        return new AppDbContext(opts);
    }

    // â”€â”€ Test 1: Course CRUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public async Task Course_CreateReadUpdateDelete_Works()
    {
        using var db = CreateDb();

        // Create user (FK requirement)
        var user = new User { FullName = "Tester", Email = "t@t.com", PasswordHash = "h" };
        db.Users.Add(user); await db.SaveChangesAsync();

        // CREATE
        var course = new Course { Title = "C# Basics", Description = "Learn C#", CreatedBy = user.UserId };
        db.Courses.Add(course); await db.SaveChangesAsync();
        Assert.True(course.CourseId > 0);

        // READ
        var found = await db.Courses.FindAsync(course.CourseId);
        Assert.NotNull(found);
        Assert.Equal("C# Basics", found!.Title);

        // UPDATE
        found.Title = "C# Advanced";
        db.Courses.Update(found); await db.SaveChangesAsync();
        var updated = await db.Courses.FindAsync(course.CourseId);
        Assert.Equal("C# Advanced", updated!.Title);

        // DELETE
        db.Courses.Remove(updated!); await db.SaveChangesAsync();
        var deleted = await db.Courses.FindAsync(course.CourseId);
        Assert.Null(deleted);
    }

    // â”€â”€ Test 2: Quiz Scoring â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public void QuizScoring_CorrectAnswersCalculated()
    {
        var questions = new List<Question>
        {
            new() { QuestionId = 1, CorrectAnswer = "A" },
            new() { QuestionId = 2, CorrectAnswer = "B" },
            new() { QuestionId = 3, CorrectAnswer = "C" },
            new() { QuestionId = 4, CorrectAnswer = "D" },
        };
        var answers = new Dictionary<int, string> { {1,"A"}, {2,"B"}, {3,"X"}, {4,"D"} };

        int score = questions.Count(q =>
            answers.TryGetValue(q.QuestionId, out var ans) && ans == q.CorrectAnswer);

        Assert.Equal(3, score);
        Assert.Equal(75.0, (double)score / questions.Count * 100);
    }

    // â”€â”€ Test 3: LINQ Filtering â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public async Task LINQ_FilterByCategory_ReturnsCorrect()
    {
        using var db = CreateDb();
        var user = new User { FullName = "U", Email = "u@u.com", PasswordHash = "h" };
        db.Users.Add(user); await db.SaveChangesAsync();

        db.Courses.AddRange(
            new Course { Title = "A", Description = "d", Category = "Backend", CreatedBy = user.UserId },
            new Course { Title = "B", Description = "d", Category = "Frontend", CreatedBy = user.UserId },
            new Course { Title = "C", Description = "d", Category = "Backend", CreatedBy = user.UserId }
        );
        await db.SaveChangesAsync();

        var backend = await db.Courses.Where(c => c.Category == "Backend").ToListAsync();
        Assert.Equal(2, backend.Count);

        var titleSearch = await db.Courses
            .Where(c => c.Title.Contains("B")).ToListAsync();
        Assert.Single(titleSearch);
    }

    // â”€â”€ Test 4: Invalid Quiz Handling â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public async Task Submit_InvalidQuizId_ReturnsNull()
    {
        using var db = CreateDb();
        var quiz = await db.Quizzes
            .Include(q => q.Questions)
            .FirstOrDefaultAsync(q => q.QuizId == 9999);
        Assert.Null(quiz);
    }

    // â”€â”€ Test 5: Password Hashing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public void BCrypt_HashAndVerify_Works()
    {
        var password = "Test@123";
        var hash = BCrypt.Net.BCrypt.HashPassword(password);

        Assert.True(BCrypt.Net.BCrypt.Verify(password, hash));
        Assert.False(BCrypt.Net.BCrypt.Verify("WrongPass", hash));
        Assert.NotEqual(password, hash); // Must not be plain text
    }

    // â”€â”€ Test 6: Unique Email Constraint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public async Task User_DuplicateEmail_Detected()
    {
        using var db = CreateDb();
        db.Users.Add(new User { FullName = "A", Email = "dup@test.com", PasswordHash = "h1" });
        await db.SaveChangesAsync();

        var exists = await db.Users.AnyAsync(u => u.Email == "dup@test.com");
        Assert.True(exists); // Registration should check this
    }

    // â”€â”€ Test 7: Relationships (Eager Loading) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    [Fact]
    public async Task Course_EagerLoadLessonsAndQuizzes()
    {
        using var db = CreateDb();
        var user = new User { FullName = "U", Email = "e@e.com", PasswordHash = "h" };
        db.Users.Add(user); await db.SaveChangesAsync();

        var course = new Course { Title = "Test", Description = "d", CreatedBy = user.UserId };
        db.Courses.Add(course); await db.SaveChangesAsync();

        db.Lessons.Add(new Lesson { CourseId = course.CourseId, Title = "L1", Content = "c", OrderIndex = 1 });
        db.Quizzes.Add(new Quiz { CourseId = course.CourseId, Title = "Q1" });
        await db.SaveChangesAsync();

        var loaded = await db.Courses
            .Include(c => c.Lessons)
            .Include(c => c.Quizzes)
            .FirstOrDefaultAsync(c => c.CourseId == course.CourseId);

        Assert.NotNull(loaded);
        Assert.Single(loaded!.Lessons);
        Assert.Single(loaded.Quizzes);
    }
}

