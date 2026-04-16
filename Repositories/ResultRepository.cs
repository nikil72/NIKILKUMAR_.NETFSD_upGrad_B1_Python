using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class ResultRepository : IResultRepository
{
    private readonly AppDbContext _db;
    public ResultRepository(AppDbContext db) => _db = db;

    public async Task<IEnumerable<Result>> GetByUserAsync(int userId) =>
        await _db.Results.AsNoTracking()
            .Include(r => r.Quiz).ThenInclude(q => q!.Course)
            .Where(r => r.UserId == userId)
            .OrderByDescending(r => r.AttemptDate)
            .ToListAsync();

    public async Task<Result> CreateAsync(Result result)
    {
        _db.Results.Add(result);
        await _db.SaveChangesAsync();
        return result;
    }

    public async Task<double> GetAverageScoreAsync()
    {
        if (!await _db.Results.AnyAsync()) return 0;
        return await _db.Results.AverageAsync(r => (double)r.Score / r.TotalQuestions * 100);
    }

    public async Task<IEnumerable<Result>> GetAboveAverageAsync()
    {
        var avg = await GetAverageScoreAsync();
        return await _db.Results.AsNoTracking()
            .Include(r => r.User)
            .Include(r => r.Quiz)
            .Where(r => (double)r.Score / r.TotalQuestions * 100 > avg)
            .ToListAsync();
    }
}
