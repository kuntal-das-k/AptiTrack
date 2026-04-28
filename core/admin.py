"""
AptiTrack Django Admin Configuration
"""
from django.contrib import admin
from .models import (
    UserProfile, Category, CompanyTag, Question,
    Quiz, QuizAttempt, UserAnswer, Bookmark
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_xp', 'streak_count', 'longest_streak', 'last_active_date')
    list_filter = ('last_active_date',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'icon', 'color')


@admin.register(CompanyTag)
class CompanyTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class QuestionCompanyInline(admin.TabularInline):
    model = Question.companies.through
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'category', 'difficulty', 'correct_answer', 'times_attempted', 'success_rate_display')
    list_filter = ('category', 'difficulty', 'companies')
    search_fields = ('text', 'explanation')
    list_editable = ('difficulty',)
    list_per_page = 25
    readonly_fields = ('times_attempted', 'times_correct', 'created_at', 'updated_at')
    fieldsets = (
        ('Question', {
            'fields': ('text', 'category', 'difficulty')
        }),
        ('Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')
        }),
        ('Explanation', {
            'fields': ('explanation',)
        }),
        ('Companies', {
            'fields': ('companies',)
        }),
        ('Stats', {
            'fields': ('times_attempted', 'times_correct', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('companies',)

    def short_text(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    short_text.short_description = 'Question'

    def success_rate_display(self, obj):
        return f"{obj.success_rate}%"
    success_rate_display.short_description = 'Success Rate'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'company', 'num_questions', 'time_limit', 'is_active')
    list_filter = ('category', 'company', 'is_active')
    list_editable = ('is_active',)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'score', 'total_questions', 'accuracy_display', 'time_formatted', 'started_at')
    list_filter = ('category', 'is_practice', 'started_at')
    search_fields = ('user__username',)
    readonly_fields = ('user', 'quiz', 'category', 'started_at', 'finished_at', 'score', 'total_questions', 'time_taken_seconds', 'xp_earned')

    def accuracy_display(self, obj):
        return f"{obj.accuracy}%"
    accuracy_display.short_description = 'Accuracy'

    def time_formatted(self, obj):
        return obj.time_formatted
    time_formatted.short_description = 'Time'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question_short', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)

    def question_short(self, obj):
        return obj.question.text[:50]
    question_short.short_description = 'Question'


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

    def question_short(self, obj):
        return obj.question.text[:50]
    question_short.short_description = 'Question'


# Customize admin site
admin.site.site_header = 'AptiTrack Administration'
admin.site.site_title = 'AptiTrack Admin'
admin.site.index_title = 'Platform Management'
