using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class QuizRepository : IQuizRepository
{
    private readonly AppDbContext _db;
    public QuizRepository(AppDbContext db) => _db = db;

    public async Task<Quiz?> GetByIdAsync(int id) =>
        await _db.Quizzes.AsNoTracking()
            .Include(q => q.Questions)
            .Include(q => q.Course)
            .FirstOrDefaultAsync(q => q.QuizId == id);

    public async Task<IEnumerable<Quiz>> GetByCourseAsync(int courseId) =>
        await _db.Quizzes.AsNoTracking()
            .Include(q => q.Questions)
            .Where(q => q.CourseId == courseId)
            .ToListAsync();

    public async Task<Quiz> CreateAsync(Quiz quiz)
    {
        _db.Quizzes.Add(quiz);
        await _db.SaveChangesAsync();
        return quiz;
    }
}
