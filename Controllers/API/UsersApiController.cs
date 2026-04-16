using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Services.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace ELearnPlatform.Controllers.API;

/// <summary>Manage user accounts</summary>
[Route("api/users")]
[ApiController]
[Produces("application/json")]
[Tags("Users")]
public class UsersApiController : ControllerBase
{
    private readonly IUserService _service;
    public UsersApiController(IUserService service) => _service = service;

    /// <summary>Register a new user</summary>
    /// <param name="dto">Registration data (FullName, Email, Password)</param>
    /// <response code="201">User registered successfully</response>
    /// <response code="400">Email already in use or validation error</response>
    [HttpPost("register")]
    [ProducesResponseType(typeof(UserDto), 201)]
    [ProducesResponseType(400)]
    public async Task<IActionResult> Register([FromBody] RegisterDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var user = await _service.RegisterAsync(dto);
        return user == null
            ? BadRequest(new { message = "Email already in use." })
            : Created("", user);
    }

    /// <summary>Get user by ID</summary>
    /// <param name="id">User ID</param>
    /// <response code="200">User data (no password hash exposed)</response>
    /// <response code="404">User not found</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(UserDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> GetById(int id)
    {
        var user = await _service.GetByIdAsync(id);
        return user == null ? NotFound() : Ok(user);
    }

    /// <summary>Update user profile</summary>
    /// <param name="id">User ID</param>
    /// <param name="dto">Updated name and email</param>
    /// <response code="200">User updated</response>
    /// <response code="404">User not found</response>
    [HttpPut("{id}")]
    [ProducesResponseType(typeof(UserDto), 200)]
    [ProducesResponseType(404)]
    public async Task<IActionResult> Update(int id, [FromBody] UpdateUserDto dto)
    {
        if (!ModelState.IsValid) return BadRequest(ModelState);
        var updated = await _service.UpdateAsync(id, dto);
        return updated == null ? NotFound() : Ok(updated);
    }
}
