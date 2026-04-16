using ELearnPlatform.Models.Entities;

namespace ELearnPlatform.Repositories.Interfaces;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id);
    Task<User?> GetByEmailAsync(string email);
    Task<IEnumerable<User>> GetAllAsync();
    Task<User> CreateAsync(User user);
    Task<User> UpdateAsync(User user);
    Task DeleteAsync(int id);
}

public interface ICourseRepository
{
    Task<Course?> GetByIdAsync(int id);
    Task<IEnumerable<Course>> GetAllAsync();
    Task<IEnumerable<Course>> GetByUserAsync(int userId);
    Task<Course> CreateAsync(Course course);
    Task<Course> UpdateAsync(Course course);
    Task DeleteAsync(int id);
}

public interface ILessonRepository
{
    Task<Lesson?> GetByIdAsync(int id);
    Task<IEnumerable<Lesson>> GetByCourseAsync(int courseId);
    Task<Lesson> CreateAsync(Lesson lesson);
    Task<Lesson> UpdateAsync(Lesson lesson);
    Task DeleteAsync(int id);
}

public interface IQuizRepository
{
    Task<Quiz?> GetByIdAsync(int id);
    Task<IEnumerable<Quiz>> GetByCourseAsync(int courseId);
    Task<Quiz> CreateAsync(Quiz quiz);
}

public interface IQuestionRepository
{
    Task<IEnumerable<Question>> GetByQuizAsync(int quizId);
    Task<Question> CreateAsync(Question question);
}

public interface IResultRepository
{
    Task<IEnumerable<Result>> GetByUserAsync(int userId);
    Task<Result> CreateAsync(Result result);
    Task<double> GetAverageScoreAsync();
    Task<IEnumerable<Result>> GetAboveAverageAsync();
}
