using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services.Interfaces;

namespace ELearnPlatform.Services;

public class ResultService : IResultService
{
    private readonly IResultRepository _repo;
    public ResultService(IResultRepository repo) => _repo = repo;

    public async Task<IEnumerable<ResultDto>> GetByUserAsync(int userId)
    {
        var results = await _repo.GetByUserAsync(userId);
        return results.Select(r => new ResultDto
        {
            ResultId = r.ResultId,
            QuizTitle = r.Quiz?.Title ?? "",
            CourseTitle = r.Quiz?.Course?.Title ?? "",
            Score = r.Score,
            TotalQuestions = r.TotalQuestions,
            Percentage = r.TotalQuestions > 0 ? (double)r.Score / r.TotalQuestions * 100 : 0,
            AttemptDate = r.AttemptDate
        });
    }
}
