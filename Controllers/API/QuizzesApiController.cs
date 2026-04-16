using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers.API;

/// <summary>Manage quizzes, questions and quiz submissions</summary>
[Route("api")]
[ApiController]
[Produces("application/json")]
[Tags("Quizzes")]
public class QuizzesApiController : ControllerBase
{
    private readonly IQuizService _service;
    public QuizzesApiController(IQuizService service) => _service = service;

    /// <summary>Get all quizzes for a course</summary>
    /// <param name="courseId">Course ID</param>
    /// <response code="200">List of quizzes with question counts</response>
    [HttpGet("quizzes/{courseId}")]
    [ProducesResponseType(typeof(IEnumerable<QuizDto>), 200)]
    public async Task<IActionResult> GetByCourse(int courseId) =>
        Ok(await _service.GetByCourseAsync(courseId));

    /// <summary>Create a new quiz</summary>
    /// <param name="dto">Quiz data (CourseId + Title)</param>
    /// <response code="201">Quiz created</response>
    /// <response code="400">Validation error</response>
    [HttpPost("quizzes")]
    [ProducesResponseType(typeof(QuizDto), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> Create([FromBody] CreateQuizDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        return Created("", await _service.CreateAsync(dto));
    }

    /// <summary>Get all questions for a quiz (answers hidden)</summary>
    /// <param name="quizId">Quiz ID</param>
    /// <response code="200">List of questions without correct answers</response>
    [HttpGet("quizzes/{quizId}/questions")]
    [ProducesResponseType(typeof(IEnumerable<QuestionDto>), 200)]
    public async Task<IActionResult> GetQuestions(int quizId) =>
        Ok(await _service.GetQuestionsAsync(quizId));

    /// <summary>Add a question to a quiz</summary>
    /// <param name="dto">Question data with all options and the correct answer key (A/B/C/D)</param>
    /// <response code="201">Question added</response>
    /// <response code="400">Validation error</response>
    [HttpPost("questions")]
    [ProducesResponseType(typeof(QuestionDto), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> AddQuestion([FromBody] CreateQuestionDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        return Created("", await _service.AddQuestionAsync(dto));
    }

    /// <summary>Submit quiz answers and get scored result</summary>
    /// <param name="quizId">Quiz ID</param>
    /// <param name="dto">Answers map: { QuestionId: "A"|"B"|"C"|"D" }</param>
    /// <response code="200">Result with score and percentage</response>
    /// <response code="404">Quiz not found</response>
    [HttpPost("quizzes/{quizId}/submit")]
    [ProducesResponseType(typeof(ResultDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Submit(int quizId, [FromBody] QuizSubmitDto dto)
    {
        dto.QuizId = quizId;
        try
        {
            var result = await _service.SubmitQuizAsync(dto);
            return Ok(result);
        }
        catch (InvalidOperationException ex)
        {
            return NotFound(new { message = ex.Message });
        }
    }

    /// <summary>Get all quiz results for a user</summary>
    /// <param name="userId">User ID</param>
    /// <response code="200">List of quiz results with scores and dates</response>
    [HttpGet("results/{userId}")]
    [ProducesResponseType(typeof(IEnumerable<ResultDto>), 200)]
    public async Task<IActionResult> GetResults(int userId, [FromServices] IResultService rs) =>
        Ok(await rs.GetByUserAsync(userId));
}
