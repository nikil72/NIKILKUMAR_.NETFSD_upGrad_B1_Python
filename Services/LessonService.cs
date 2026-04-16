using AutoMapper;
using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services.Interfaces;

namespace ELearnPlatform.Services;

public class LessonService : ILessonService
{
    private readonly ILessonRepository _repo;
    private readonly IMapper _mapper;
    public LessonService(ILessonRepository repo, IMapper mapper) { _repo = repo; _mapper = mapper; }

    public async Task<IEnumerable<LessonDto>> GetByCourseAsync(int courseId) =>
        _mapper.Map<IEnumerable<LessonDto>>(await _repo.GetByCourseAsync(courseId));

    public async Task<LessonDto> CreateAsync(CreateLessonDto dto)
    {
        var lesson = _mapper.Map<Lesson>(dto);
        return _mapper.Map<LessonDto>(await _repo.CreateAsync(lesson));
    }

    public async Task<LessonDto?> UpdateAsync(int id, CreateLessonDto dto)
    {
        var lesson = await _repo.GetByIdAsync(id);
        if (lesson == null) return null;
        lesson.Title = dto.Title; lesson.Content = dto.Content; lesson.OrderIndex = dto.OrderIndex;
        return _mapper.Map<LessonDto>(await _repo.UpdateAsync(lesson));
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var lesson = await _repo.GetByIdAsync(id);
        if (lesson == null) return false;
        await _repo.DeleteAsync(id);
        return true;
    }
}
