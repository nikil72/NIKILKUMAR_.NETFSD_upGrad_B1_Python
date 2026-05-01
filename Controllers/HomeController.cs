using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers;

public class HomeController : Controller
{
    private readonly ICourseService _courseService;
    private readonly IResultService _resultService;

    public HomeController(ICourseService cs, IResultService rs)
    { _courseService = cs; _resultService = rs; }

    public async Task<IActionResult> Index()
    {
        var courses = await _courseService.GetAllAsync();
        ViewBag.Courses = courses;
        ViewBag.CourseCount = courses.Count();
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId.HasValue)
        {
            var results = await _resultService.GetByUserAsync(userId.Value);
            var resultList = results.ToList();
            ViewBag.QuizzesTaken = resultList.Count;
            ViewBag.AvgScore = resultList.Any() ? resultList.Average(r => r.Percentage) : 0;
        }
        return View();
    }

    [HttpGet] public IActionResult Login() => View();
    [HttpGet] public IActionResult Register() => View();

    [HttpPost]
    public async Task<IActionResult> Login(string email, string password,
        [FromServices] IUserService userService)
    {
        var user = await userService.LoginAsync(new LoginDto { Email = email, Password = password });
        if (user == null) { ViewBag.Error = "Invalid email or password."; return View(); }
        HttpContext.Session.SetInt32("UserId", user.UserId);
        HttpContext.Session.SetString("UserName", user.FullName);
        return RedirectToAction("Index");
    }

    [HttpPost]
    public async Task<IActionResult> Register(string fullName, string email, string password,
        [FromServices] IUserService userService)
    {
        var user = await userService.RegisterAsync(new RegisterDto
            { FullName = fullName, Email = email, Password = password });
        if (user == null) { ViewBag.Error = "Email already in use."; return View(); }
        HttpContext.Session.SetInt32("UserId", user.UserId);
        HttpContext.Session.SetString("UserName", user.FullName);
        return RedirectToAction("Index");
    }

    public IActionResult Logout()
    {
        HttpContext.Session.Clear();
        return RedirectToAction("Index");
    }

    public IActionResult Error() => View();
}
