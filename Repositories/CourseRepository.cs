using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class CourseRepository : ICourseRepository
{
    private readonly AppDbContext _db;
    public CourseRepository(AppDbContext db) => _db = db;

    public async Task<Course?> GetByIdAsync(int id) =>
        await _db.Courses.AsNoTracking()
            .Include(c => c.Creator)
            .Include(c => c.Lessons)
            .Include(c => c.Quizzes).ThenInclude(q => q.Questions)
            .FirstOrDefaultAsync(c => c.CourseId == id);

    public async Task<IEnumerable<Course>> GetAllAsync() =>
        await _db.Courses.AsNoTracking()
            .Include(c => c.Creator)
            .Include(c => c.Lessons)
            .Include(c => c.Quizzes)
            .OrderByDescending(c => c.CreatedAt)
            .ToListAsync();

    public async Task<IEnumerable<Course>> GetByUserAsync(int userId) =>
        await _db.Courses.AsNoTracking()
            .Where(c => c.CreatedBy == userId)
            .Include(c => c.Lessons)
            .Include(c => c.Quizzes)
            .ToListAsync();

    public async Task<Course> CreateAsync(Course course)
    {
        _db.Courses.Add(course);
        await _db.SaveChangesAsync();
        return course;
    }

    public async Task<Course> UpdateAsync(Course course)
    {
        _db.Courses.Update(course);
        await _db.SaveChangesAsync();
        return course;
    }

    public async Task DeleteAsync(int id)
    {
        var course = await _db.Courses.FindAsync(id);
        if (course != null) { _db.Courses.Remove(course); await _db.SaveChangesAsync(); }
    }
}
