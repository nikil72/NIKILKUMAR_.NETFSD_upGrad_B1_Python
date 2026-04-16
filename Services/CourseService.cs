using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services.Interfaces;

namespace ELearnPlatform.Services;

public class CourseService : ICourseService
{
    private readonly ICourseRepository _repo;
    public CourseService(ICourseRepository repo) => _repo = repo;

    private static CourseDto ToDto(Course c) => new()
    {
        CourseId = c.CourseId, Title = c.Title, Description = c.Description,
        ImageUrl = c.ImageUrl, Category = c.Category,
        CreatorName = c.Creator?.FullName ?? "Unknown",
        CreatedAt = c.CreatedAt,
        LessonCount = c.Lessons.Count,
        QuizCount = c.Quizzes.Count
    };

    public async Task<IEnumerable<CourseDto>> GetAllAsync() =>
        (await _repo.GetAllAsync()).Select(ToDto);

    public async Task<CourseDto?> GetByIdAsync(int id)
    {
        var c = await _repo.GetByIdAsync(id);
        return c == null ? null : ToDto(c);
    }

    public async Task<CourseDto> CreateAsync(CreateCourseDto dto, int userId)
    {
        var course = new Course
        {
            Title = dto.Title, Description = dto.Description,
            ImageUrl = dto.ImageUrl, Category = dto.Category, CreatedBy = userId
        };
        var created = await _repo.CreateAsync(course);
        return (await GetByIdAsync(created.CourseId))!;
    }

    public async Task<CourseDto?> UpdateAsync(int id, UpdateCourseDto dto)
    {
        var course = await _repo.GetByIdAsync(id);
        if (course == null) return null;
        course.Title = dto.Title; course.Description = dto.Description;
        course.ImageUrl = dto.ImageUrl; course.Category = dto.Category;
        await _repo.UpdateAsync(course);
        return await GetByIdAsync(id);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var course = await _repo.GetByIdAsync(id);
        if (course == null) return false;
        await _repo.DeleteAsync(id);
        return true;
    }
}
