using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers;

public class CoursesController : Controller
{
    private readonly ICourseService _courseService;
    private readonly ILessonService _lessonService;
    private readonly IQuizService _quizService;

    public CoursesController(ICourseService cs, ILessonService ls, IQuizService qs)
    { _courseService = cs; _lessonService = ls; _quizService = qs; }

    public async Task<IActionResult> Index(string? search, string? category)
    {
        var courses = await _courseService.GetAllAsync();
        if (!string.IsNullOrWhiteSpace(search))
            courses = courses.Where(c => c.Title.Contains(search, StringComparison.OrdinalIgnoreCase)
                || c.Description.Contains(search, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrWhiteSpace(category))
            courses = courses.Where(c => c.Category == category);
        ViewBag.Search = search;
        ViewBag.Category = category;
        return View(courses);
    }

    public async Task<IActionResult> Details(int id)
    {
        var course = await _courseService.GetByIdAsync(id);
        if (course == null) return NotFound();
        ViewBag.Lessons = await _lessonService.GetByCourseAsync(id);
        ViewBag.Quizzes = await _quizService.GetByCourseAsync(id);
        return View(course);
    }

    [HttpGet]
    public IActionResult Create()
    {
        if (HttpContext.Session.GetInt32("UserId") == null) return RedirectToAction("Login", "Home");
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Create(string title, string description,
        string? category, string? imageUrl)
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null) return RedirectToAction("Login", "Home");
        var dto = new CreateCourseDto { Title = title, Description = description,
            Category = category, ImageUrl = imageUrl };
        var created = await _courseService.CreateAsync(dto, userId.Value);
        return RedirectToAction("Details", new { id = created.CourseId });
    }

    [HttpPost]
    public async Task<IActionResult> Delete(int id)
    {
        await _courseService.DeleteAsync(id);
        return RedirectToAction("Index");
    }
}
