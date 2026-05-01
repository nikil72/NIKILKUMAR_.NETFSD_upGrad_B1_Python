using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers.API;

/// <summary>Manage courses</summary>
[Route("api/courses")]
[ApiController]
[Produces("application/json")]
[Tags("Courses")]
public class CoursesApiController : ControllerBase
{
    private readonly ICourseService _service;
    public CoursesApiController(ICourseService service) => _service = service;

    /// <summary>Get all courses</summary>
    /// <returns>List of all courses with lesson/quiz counts</returns>
    /// <response code="200">Returns the list of courses</response>
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<CourseDto>), 200)]
    public async Task<IActionResult> GetAll() => Ok(await _service.GetAllAsync());

    /// <summary>Get a course by ID</summary>
    /// <param name="id">Course ID</param>
    /// <response code="200">Course found</response>
    /// <response code="404">Course not found</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(CourseDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetById(int id)
    {
        var course = await _service.GetByIdAsync(id);
        return course == null ? NotFound(new { message = "Course not found" }) : Ok(course);
    }

    /// <summary>Create a new course</summary>
    /// <param name="dto">Course data</param>
    /// <response code="201">Course created successfully</response>
    /// <response code="400">Validation error</response>
    [HttpPost]
    [ProducesResponseType(typeof(CourseDto), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> Create([FromBody] CreateCourseDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var created = await _service.CreateAsync(dto, userId: 1);
        return CreatedAtAction(nameof(GetById), new { id = created.CourseId }, created);
    }

    /// <summary>Update an existing course</summary>
    /// <param name="id">Course ID</param>
    /// <param name="dto">Updated course data</param>
    /// <response code="200">Course updated</response>
    /// <response code="404">Course not found</response>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(CourseDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Update(int id, [FromBody] UpdateCourseDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var updated = await _service.UpdateAsync(id, dto);
        return updated == null ? NotFound(new { message = "Course not found" }) : Ok(updated);
    }

    /// <summary>Delete a course</summary>
    /// <param name="id">Course ID</param>
    /// <response code="204">Deleted successfully</response>
    /// <response code="404">Course not found</response>
    [HttpDelete("{id}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Delete(int id)
    {
        var deleted = await _service.DeleteAsync(id);
        return deleted ? NoContent() : NotFound(new { message = "Course not found" });
    }
}
