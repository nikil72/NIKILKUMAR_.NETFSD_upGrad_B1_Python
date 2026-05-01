using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers.API;

/// <summary>Manage lessons within courses</summary>
[Route("api")]
[ApiController]
[Produces("application/json")]
[Tags("Lessons")]
public class LessonsApiController : ControllerBase
{
    private readonly ILessonService _service;
    public LessonsApiController(ILessonService service) => _service = service;

    /// <summary>Get all lessons for a course</summary>
    /// <param name="courseId">Course ID</param>
    /// <response code="200">Ordered list of lessons</response>
    [HttpGet("courses/{courseId}/lessons")]
    [ProducesResponseType(typeof(IEnumerable<LessonDto>), 200)]
    public async Task<IActionResult> GetByCourse(int courseId) =>
        Ok(await _service.GetByCourseAsync(courseId));

    /// <summary>Create a new lesson</summary>
    /// <param name="dto">Lesson data including CourseId, Title, Content, OrderIndex</param>
    /// <response code="201">Lesson created</response>
    /// <response code="400">Validation error</response>
    [HttpPost("lessons")]
    [ProducesResponseType(typeof(LessonDto), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> Create([FromBody] CreateLessonDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var created = await _service.CreateAsync(dto);
        return Created($"/api/lessons/{created.LessonId}", created);
    }

    /// <summary>Update a lesson</summary>
    /// <param name="id">Lesson ID</param>
    /// <param name="dto">Updated lesson data</param>
    /// <response code="200">Lesson updated</response>
    /// <response code="404">Lesson not found</response>
    [HttpPut("lessons/{id}")]
    [ProducesResponseType(typeof(LessonDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Update(int id, [FromBody] CreateLessonDto dto)
    {
        var updated = await _service.UpdateAsync(id, dto);
        return updated == null ? NotFound() : Ok(updated);
    }

    /// <summary>Delete a lesson</summary>
    /// <param name="id">Lesson ID</param>
    /// <response code="204">Deleted successfully</response>
    /// <response code="404">Lesson not found</response>
    [HttpDelete("lessons/{id}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Delete(int id)
    {
        var deleted = await _service.DeleteAsync(id);
        return deleted ? NoContent() : NotFound();
    }
}
