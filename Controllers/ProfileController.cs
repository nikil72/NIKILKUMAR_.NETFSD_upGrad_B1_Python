using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers;

public class ProfileController : Controller
{
    private readonly IUserService _userService;
    private readonly IResultService _resultService;
    private readonly ICourseService _courseService;

    public ProfileController(IUserService us, IResultService rs, ICourseService cs)
    { _userService = us; _resultService = rs; _courseService = cs; }

    public async Task<IActionResult> Index()
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null) return RedirectToAction("Login", "Home");
        ViewBag.User = await _userService.GetByIdAsync(userId.Value);
        ViewBag.Results = await _resultService.GetByUserAsync(userId.Value);
        ViewBag.MyCourses = await _courseService.GetAllAsync();
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Update(string fullName, string email)
    {
        var userId = HttpContext.Session.GetInt32("UserId");
        if (userId == null) return RedirectToAction("Login", "Home");
        await _userService.UpdateAsync(userId.Value, new UpdateUserDto { FullName = fullName, Email = email });
        HttpContext.Session.SetString("UserName", fullName);
        TempData["Success"] = "Profile updated successfully!";
        return RedirectToAction("Index");
    }
}
