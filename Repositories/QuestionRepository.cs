using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class QuestionRepository : IQuestionRepository
{
    private readonly AppDbContext _db;
    public QuestionRepository(AppDbContext db) => _db = db;

    public async Task<IEnumerable<Question>> GetByQuizAsync(int quizId) =>
        await _db.Questions.AsNoTracking()
            .Where(q => q.QuizId == quizId)
            .ToListAsync();

    public async Task<Question> CreateAsync(Question question)
    {
        _db.Questions.Add(question);
        await _db.SaveChangesAsync();
        return question;
    }
}
