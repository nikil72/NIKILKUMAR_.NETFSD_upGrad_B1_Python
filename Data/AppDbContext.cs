using ELearnPlatform.Models.Entities;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Course> Courses => Set<Course>();
    public DbSet<Lesson> Lessons => Set<Lesson>();
    public DbSet<Quiz> Quizzes => Set<Quiz>();
    public DbSet<Question> Questions => Set<Question>();
    public DbSet<Result> Results => Set<Result>();

    protected override void OnModelCreating(ModelBuilder mb)
    {
        mb.Entity<User>()
            .HasIndex(u => u.Email).IsUnique();

        mb.Entity<Course>()
            .HasOne(c => c.Creator)
            .WithMany(u => u.Courses)
            .HasForeignKey(c => c.CreatedBy)
            .OnDelete(DeleteBehavior.Cascade);

        mb.Entity<Lesson>()
            .HasOne(l => l.Course)
            .WithMany(c => c.Lessons)
            .HasForeignKey(l => l.CourseId)
            .OnDelete(DeleteBehavior.Cascade);

        mb.Entity<Quiz>()
            .HasOne(q => q.Course)
            .WithMany(c => c.Quizzes)
            .HasForeignKey(q => q.CourseId)
            .OnDelete(DeleteBehavior.Cascade);

        mb.Entity<Question>()
            .HasOne(q => q.Quiz)
            .WithMany(qz => qz.Questions)
            .HasForeignKey(q => q.QuizId)
            .OnDelete(DeleteBehavior.Cascade);

        mb.Entity<Result>()
            .HasOne(r => r.User)
            .WithMany(u => u.Results)
            .HasForeignKey(r => r.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        mb.Entity<Result>()
            .HasOne(r => r.Quiz)
            .WithMany(q => q.Results)
            .HasForeignKey(r => r.QuizId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
