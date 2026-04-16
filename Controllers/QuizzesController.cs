using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers;

public class QuizzesController : Controller
{
    private readonly IQuizService _quizService;
    public QuizzesController(IQuizService quizService) => _quizService = quizService;

    public async Task<IActionResult> Take(int id)
    {
        var questions = await _quizService.GetQuestionsAsync(id);
        var qList = questions.ToList();
        if (!qList.Any()) return RedirectToAction("Index", "Courses");
        ViewBag.QuizId = id;
        ViewBag.Questions = qList;
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Submit(int quizId, Dictionary<string, string> answers)
    {
        var userId = HttpContext.Session.GetInt32("UserId") ?? 1;
        var parsedAnswers = new Dictionary<int, string>();
        foreach (var kvp in answers)
            if (int.TryParse(kvp.Key, out int qid)) parsedAnswers[qid] = kvp.Value;

        var dto = new QuizSubmitDto { QuizId = quizId, UserId = userId, Answers = parsedAnswers };
        try
        {
            var result = await _quizService.SubmitQuizAsync(dto);
            return View("Result", result);
        }
        catch { return RedirectToAction("Take", new { id = quizId }); }
    }
}
