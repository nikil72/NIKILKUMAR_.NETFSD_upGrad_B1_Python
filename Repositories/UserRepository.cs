using ELearnPlatform.Data;
using ELearnPlatform.Models.Entities;
using ELearnPlatform.Repositories.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace ELearnPlatform.Repositories;

public class UserRepository : IUserRepository
{
    private readonly AppDbContext _db;
    public UserRepository(AppDbContext db) => _db = db;

    public async Task<User?> GetByIdAsync(int id) =>
        await _db.Users.AsNoTracking().FirstOrDefaultAsync(u => u.UserId == id);

    public async Task<User?> GetByEmailAsync(string email) =>
        await _db.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Email == email);

    public async Task<IEnumerable<User>> GetAllAsync() =>
        await _db.Users.AsNoTracking().ToListAsync();

    public async Task<User> CreateAsync(User user)
    {
        _db.Users.Add(user);
        await _db.SaveChangesAsync();
        return user;
    }

    public async Task<User> UpdateAsync(User user)
    {
        _db.Users.Update(user);
        await _db.SaveChangesAsync();
        return user;
    }

    public async Task DeleteAsync(int id)
    {
        var user = await _db.Users.FindAsync(id);
        if (user != null) { _db.Users.Remove(user); await _db.SaveChangesAsync(); }
    }
}
