using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class LessonRepository : ILessonRepository
{
    private readonly AppDbContext _db;
    public LessonRepository(AppDbContext db) => _db = db;

    public async Task<Lesson?> GetByIdAsync(int id) =>
        await _db.Lessons.AsNoTracking().FirstOrDefaultAsync(l => l.LessonId == id);

    public async Task<IEnumerable<Lesson>> GetByCourseAsync(int courseId) =>
        await _db.Lessons.AsNoTracking()
            .Where(l => l.CourseId == courseId)
            .OrderBy(l => l.OrderIndex)
            .ToListAsync();

    public async Task<Lesson> CreateAsync(Lesson lesson)
    {
        _db.Lessons.Add(lesson);
        await _db.SaveChangesAsync();
        return lesson;
    }

    public async Task<Lesson> UpdateAsync(Lesson lesson)
    {
        _db.Lessons.Update(lesson);
        await _db.SaveChangesAsync();
        return lesson;
    }

    public async Task DeleteAsync(int id)
    {
        var lesson = await _db.Lessons.FindAsync(id);
        if (lesson != null) { _db.Lessons.Remove(lesson); await _db.SaveChangesAsync(); }
    }
}
