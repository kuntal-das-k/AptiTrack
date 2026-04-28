"""
AptiTrack Database Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class UserProfile(models.Model):
    """Extended user profile with gamification fields."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    streak_count = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    total_xp = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-total_xp']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def update_streak(self):
        """Update daily streak based on activity."""
        today = timezone.now().date()
        if self.last_active_date is None:
            self.streak_count = 1
        elif self.last_active_date == today:
            pass  # Already active today
        elif (today - self.last_active_date).days == 1:
            self.streak_count += 1
        else:
            self.streak_count = 1  # Reset streak

        if self.streak_count > self.longest_streak:
            self.longest_streak = self.streak_count

        self.last_active_date = today
        self.save()

    def add_xp(self, points):
        """Add experience points."""
        self.total_xp += points
        self.save()


class Category(models.Model):
    """Question category (Quantitative, Logical, Verbal, Data Interpretation)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📊')
    description = models.TextField(blank=True, default='')
    color = models.CharField(max_length=7, default='#3b82f6', help_text='Hex color code')
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('practice') + f'?category={self.slug}'


class CompanyTag(models.Model):
    """Company tag for filtering questions by company."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo_url = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    """Aptitude question with MCQ options."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    companies = models.ManyToManyField(CompanyTag, blank=True, related_name='questions')
    text = models.TextField(help_text='Question text (supports basic HTML)')
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')],
        help_text='Correct option letter'
    )
    explanation = models.TextField(blank=True, default='', help_text='Solution explanation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    times_attempted = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category.name}][{self.difficulty}] {self.text[:80]}..."

    @property
    def success_rate(self):
        if self.times_attempted == 0:
            return 0
        return round((self.times_correct / self.times_attempted) * 100, 1)

    @property
    def difficulty_color(self):
        colors = {'easy': '#10b981', 'medium': '#f59e0b', 'hard': '#ef4444'}
        return colors.get(self.difficulty, '#6b7280')

    @property
    def xp_value(self):
        values = {'easy': 10, 'medium': 25, 'hard': 50}
        return values.get(self.difficulty, 10)


class Quiz(models.Model):
    """Pre-configured quiz / mock test."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(CompanyTag, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.CharField(
        max_length=10,
        choices=Question.DIFFICULTY_CHOICES,
        blank=True,
        default=''
    )
    num_questions = models.IntegerField(default=20)
    time_limit = models.IntegerField(default=30, help_text='Time limit in minutes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class QuizAttempt(models.Model):
    """Record of a user taking a quiz or practice session."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    is_practice = models.BooleanField(default=False)
    xp_earned = models.IntegerField(default=0)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - Score: {self.score}/{self.total_questions}"

    @property
    def accuracy(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100, 1)

    @property
    def time_formatted(self):
        mins = self.time_taken_seconds // 60
        secs = self.time_taken_seconds % 60
        return f"{mins}m {secs}s"


class UserAnswer(models.Model):
    """Individual answer in a quiz attempt."""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_answer = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])
    is_correct = models.BooleanField(default=False)
    time_spent_seconds = models.IntegerField(default=0)

    class Meta:
        unique_together = ['attempt', 'question']

    def __str__(self):
        status = '✓' if self.is_correct else '✗'
        return f"{status} Q{self.question.id} → {self.selected_answer}"


class Bookmark(models.Model):
    """User bookmarked questions for later review."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ['user', 'question']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → Q{self.question.id}"
