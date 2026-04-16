using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services.Interfaces;
using AutoMapper;

namespace ELearnPlatform.Services;

public class UserService : IUserService
{
    private readonly IUserRepository _repo;
    private readonly IMapper _mapper;
    public UserService(IUserRepository repo, IMapper mapper) { _repo = repo; _mapper = mapper; }

    public async Task<UserDto?> RegisterAsync(RegisterDto dto)
    {
        var existing = await _repo.GetByEmailAsync(dto.Email);
        if (existing != null) return null;
        var user = new User
        {
            FullName = dto.FullName,
            Email = dto.Email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password)
        };
        var created = await _repo.CreateAsync(user);
        return _mapper.Map<UserDto>(created);
    }

    public async Task<UserDto?> LoginAsync(LoginDto dto)
    {
        var user = await _repo.GetByEmailAsync(dto.Email);
        if (user == null || !BCrypt.Net.BCrypt.Verify(dto.Password, user.PasswordHash)) return null;
        return _mapper.Map<UserDto>(user);
    }

    public async Task<UserDto?> GetByIdAsync(int id)
    {
        var user = await _repo.GetByIdAsync(id);
        return user == null ? null : _mapper.Map<UserDto>(user);
    }

    public async Task<UserDto?> UpdateAsync(int id, UpdateUserDto dto)
    {
        var user = await _repo.GetByIdAsync(id);
        if (user == null) return null;
        user.FullName = dto.FullName;
        user.Email = dto.Email;
        var updated = await _repo.UpdateAsync(user);
        return _mapper.Map<UserDto>(updated);
    }
}
