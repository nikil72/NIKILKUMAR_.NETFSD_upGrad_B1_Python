using AutoMapper;
using ELearnPlatform.Models.DTOs;
using ELearnPlatform.Models.Entities;

namespace ELearnPlatform.Mappings;

public class MappingProfile : Profile
{
    public MappingProfile()
    {
        CreateMap<User, UserDto>();
        CreateMap<Lesson, LessonDto>();
        CreateMap<CreateLessonDto, Lesson>();
        CreateMap<Question, QuestionDto>();
        CreateMap<CreateQuestionDto, Question>();
    }
}
