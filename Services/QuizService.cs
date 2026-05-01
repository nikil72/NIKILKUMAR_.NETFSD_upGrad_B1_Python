using AutoMapper;
using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services.Interfaces;

namespace ELearnPlatform.Services;

public class QuizService : IQuizService
{
    private readonly IQuizRepository _quizRepo;
    private readonly IQuestionRepository _qRepo;
    private readonly IResultRepository _resultRepo;
    private readonly IMapper _mapper;

    public QuizService(IQuizRepository quizRepo, IQuestionRepository qRepo,
        IResultRepository resultRepo, IMapper mapper)
    { _quizRepo = quizRepo; _qRepo = qRepo; _resultRepo = resultRepo; _mapper = mapper; }

    public async Task<IEnumerable<QuizDto>> GetByCourseAsync(int courseId)
    {
        var quizzes = await _quizRepo.GetByCourseAsync(courseId);
        return quizzes.Select(q => new QuizDto
        {
            QuizId = q.QuizId, CourseId = q.CourseId,
            Title = q.Title, QuestionCount = q.Questions.Count
        });
    }

    public async Task<QuizDto> CreateAsync(CreateQuizDto dto)
    {
        var quiz = new Quiz { CourseId = dto.CourseId, Title = dto.Title };
        var created = await _quizRepo.CreateAsync(quiz);
        return new QuizDto { QuizId = created.QuizId, CourseId = created.CourseId, Title = created.Title };
    }

    public async Task<IEnumerable<QuestionDto>> GetQuestionsAsync(int quizId) =>
        _mapper.Map<IEnumerable<QuestionDto>>(await _qRepo.GetByQuizAsync(quizId));

    public async Task<QuestionDto> AddQuestionAsync(CreateQuestionDto dto) =>
        _mapper.Map<QuestionDto>(await _qRepo.CreateAsync(_mapper.Map<Question>(dto)));

    public async Task<ResultDto> SubmitQuizAsync(QuizSubmitDto dto)
    {
        var quiz = await _quizRepo.GetByIdAsync(dto.QuizId)
            ?? throw new InvalidOperationException("Quiz not found");

        int score = quiz.Questions.Count(q =>
            dto.Answers.TryGetValue(q.QuestionId, out var ans) && ans == q.CorrectAnswer);

        var result = new Result
        {
            UserId = dto.UserId, QuizId = dto.QuizId,
            Score = score, TotalQuestions = quiz.Questions.Count
        };
        await _resultRepo.CreateAsync(result);

        return new ResultDto
        {
            QuizTitle = quiz.Title,
            CourseTitle = quiz.Course?.Title ?? "",
            Score = score,
            TotalQuestions = quiz.Questions.Count,
            Percentage = quiz.Questions.Count > 0 ? (double)score / quiz.Questions.Count * 100 : 0,
            AttemptDate = result.AttemptDate
        };
    }
}
