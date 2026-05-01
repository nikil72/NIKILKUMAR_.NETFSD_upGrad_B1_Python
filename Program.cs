using ELearnPlatform.Data;
using ELearnPlatform.Mappings;
using ELearnPlatform.Repositories;
using ELearnPlatform.Repositories.Interfaces;
using ELearnPlatform.Services;
using ELearnPlatform.Services.Interfaces;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using System.Reflection;

var builder = WebApplication.CreateBuilder(args);

// ── MVC + API ─────────────────────────────────────────────────────────────────
builder.Services.AddControllersWithViews();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// ── Swagger ───────────────────────────────────────────────────────────────────
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title       = "ELearn Platform API",
        Version     = "v1",
        Description = "Full-stack E-Learning REST API — ASP.NET Core 8 + SQLite + EF Core\n\n" +
                      "**Base URL:** `/api`\n\n" +
                      "Use the endpoints below to manage Courses, Lessons, Quizzes, Questions, Users and Results.",
        Contact = new OpenApiContact
        {
            Name  = "ELearn Platform",
            Email = "admin@elearn.com"
        }
    });

    // XML comments from source
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath)) options.IncludeXmlComments(xmlPath);

    // Group by tag order
    options.TagActionsBy(api => new[] { api.GroupName ?? api.ActionDescriptor.RouteValues["controller"] });
    options.DocInclusionPredicate((_, _) => true);
});

// ── SQLite ────────────────────────────────────────────────────────────────────
builder.Services.AddDbContext<AppDbContext>(o =>
    o.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// ── AutoMapper ────────────────────────────────────────────────────────────────
builder.Services.AddAutoMapper(typeof(MappingProfile));

// ── Repositories ──────────────────────────────────────────────────────────────
builder.Services.AddScoped<IUserRepository,     UserRepository>();
builder.Services.AddScoped<ICourseRepository,   CourseRepository>();
builder.Services.AddScoped<ILessonRepository,   LessonRepository>();
builder.Services.AddScoped<IQuizRepository,     QuizRepository>();
builder.Services.AddScoped<IQuestionRepository, QuestionRepository>();
builder.Services.AddScoped<IResultRepository,   ResultRepository>();

// ── Services ──────────────────────────────────────────────────────────────────
builder.Services.AddScoped<IUserService,   UserService>();
builder.Services.AddScoped<ICourseService, CourseService>();
builder.Services.AddScoped<ILessonService, LessonService>();
builder.Services.AddScoped<IQuizService,   QuizService>();
builder.Services.AddScoped<IResultService, ResultService>();

// ── Session ───────────────────────────────────────────────────────────────────
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(o =>
{
    o.IdleTimeout        = TimeSpan.FromMinutes(60);
    o.Cookie.HttpOnly    = true;
    o.Cookie.IsEssential = true;
});
builder.Services.AddHttpContextAccessor();

var app = builder.Build();

// ── Seed DB ───────────────────────────────────────────────────────────────────
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DbSeeder.Seed(db);
}

// ── Middleware ────────────────────────────────────────────────────────────────
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "ELearn API v1");
        c.RoutePrefix          = "swagger";
        c.DocumentTitle        = "ELearn Platform API";
        c.DefaultModelsExpandDepth(2);
        c.DefaultModelExpandDepth(2);
        c.DisplayRequestDuration();
        c.EnableFilter();
        c.EnableDeepLinking();
        c.InjectStylesheet("/css/swagger-custom.css");
    });
}
else
{
    // Also expose Swagger in production (optional — remove if unwanted)
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "ELearn API v1");
        c.RoutePrefix   = "swagger";
        c.DocumentTitle = "ELearn Platform API";
    });
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseStaticFiles();
app.UseRouting();
app.UseSession();
app.UseAuthorization();

app.MapControllers();
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
