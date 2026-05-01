using System.ComponentModel.DataAnnotations;

namespace ELearnPlatform.Models.DTOs;

public class RegisterDto
{
    [Required] public string FullName { get; set; } = string.Empty;
    [Required, EmailAddress] public string Email { get; set; } = string.Empty;
    [Required, MinLength(6)] public string Password { get; set; } = string.Empty;
}

public class LoginDto
{
    [Required, EmailAddress] public string Email { get; set; } = string.Empty;
    [Required] public string Password { get; set; } = string.Empty;
}

public class UserDto
{
    public int UserId { get; set; }
    public string FullName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}

public class UpdateUserDto
{
    [Required] public string FullName { get; set; } = string.Empty;
    [Required, EmailAddress] public string Email { get; set; } = string.Empty;
}

public class CourseDto
{
    public int CourseId { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public string? Category { get; set; }
    public string CreatorName { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public int LessonCount { get; set; }
    public int QuizCount { get; set; }
}

public class CreateCourseDto
{
    [Required] public string Title { get; set; } = string.Empty;
    [Required] public string Description { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public string? Category { get; set; }
}

public class UpdateCourseDto
{
    [Required] public string Title { get; set; } = string.Empty;
    [Required] public string Description { get; set; } = string.Empty;
    public string? ImageUrl { get; set; }
    public string? Category { get; set; }
}

public class LessonDto
{
    public int LessonId { get; set; }
    public int CourseId { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public int OrderIndex { get; set; }
}

public class CreateLessonDto
{
    [Required] public int CourseId { get; set; }
    [Required] public string Title { get; set; } = string.Empty;
    [Required] public string Content { get; set; } = string.Empty;
    public int OrderIndex { get; set; }
}

public class QuizDto
{
    public int QuizId { get; set; }
    public int CourseId { get; set; }
    public string Title { get; set; } = string.Empty;
    public int QuestionCount { get; set; }
}

public class CreateQuizDto
{
    [Required] public int CourseId { get; set; }
    [Required] public string Title { get; set; } = string.Empty;
}

public class QuestionDto
{
    public int QuestionId { get; set; }
    public string QuestionText { get; set; } = string.Empty;
    public string OptionA { get; set; } = string.Empty;
    public string OptionB { get; set; } = string.Empty;
    public string OptionC { get; set; } = string.Empty;
    public string OptionD { get; set; } = string.Empty;
}

public class CreateQuestionDto
{
    [Required] public int QuizId { get; set; }
    [Required] public string QuestionText { get; set; } = string.Empty;
    [Required] public string OptionA { get; set; } = string.Empty;
    [Required] public string OptionB { get; set; } = string.Empty;
    [Required] public string OptionC { get; set; } = string.Empty;
    [Required] public string OptionD { get; set; } = string.Empty;
    [Required] public string CorrectAnswer { get; set; } = string.Empty;
}

public class QuizSubmitDto
{
    public int QuizId { get; set; }
    public int UserId { get; set; }
    public Dictionary<int, string> Answers { get; set; } = new();
}

public class ResultDto
{
    public int ResultId { get; set; }
    public string QuizTitle { get; set; } = string.Empty;
    public string CourseTitle { get; set; } = string.Empty;
    public int Score { get; set; }
    public int TotalQuestions { get; set; }
    public double Percentage { get; set; }
    public DateTime AttemptDate { get; set; }
}
