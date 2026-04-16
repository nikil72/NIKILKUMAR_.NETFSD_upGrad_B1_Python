using ELearnPlatform.Models.DTOs;

namespace ELearnPlatform.Services.Interfaces;

public interface IUserService
{
    Task<UserDto?> RegisterAsync(RegisterDto dto);
    Task<UserDto?> LoginAsync(LoginDto dto);
    Task<UserDto?> GetByIdAsync(int id);
    Task<UserDto?> UpdateAsync(int id, UpdateUserDto dto);
}

public interface ICourseService
{
    Task<IEnumerable<CourseDto>> GetAllAsync();
    Task<CourseDto?> GetByIdAsync(int id);
    Task<CourseDto> CreateAsync(CreateCourseDto dto, int userId);
    Task<CourseDto?> UpdateAsync(int id, UpdateCourseDto dto);
    Task<bool> DeleteAsync(int id);
}

public interface ILessonService
{
    Task<IEnumerable<LessonDto>> GetByCourseAsync(int courseId);
    Task<LessonDto> CreateAsync(CreateLessonDto dto);
    Task<LessonDto?> UpdateAsync(int id, CreateLessonDto dto);
    Task<bool> DeleteAsync(int id);
}

public interface IQuizService
{
    Task<IEnumerable<QuizDto>> GetByCourseAsync(int courseId);
    Task<QuizDto> CreateAsync(CreateQuizDto dto);
    Task<IEnumerable<QuestionDto>> GetQuestionsAsync(int quizId);
    Task<QuestionDto> AddQuestionAsync(CreateQuestionDto dto);
    Task<ResultDto> SubmitQuizAsync(QuizSubmitDto dto);
}

public interface IResultService
{
    Task<IEnumerable<ResultDto>> GetByUserAsync(int userId);
}
