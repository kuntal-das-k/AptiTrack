"""
AptiTrack Views — All view functions for the platform.
"""
import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q, Sum, F
from django.core.paginator import Paginator

from .models import (
    UserProfile, Category, CompanyTag, Question,
    Quiz, QuizAttempt, UserAnswer, Bookmark
)
from .forms import SignupForm, LoginForm, ProfileForm, QuizConfigForm


# ─── Landing Page ─────────────────────────────────────────────

def home_view(request):
    """Landing page with platform overview."""
    try:
        categories = Category.objects.annotate(
            question_count=Count('questions')
        )
        total_questions = Question.objects.count()
        total_users = UserProfile.objects.count()
        total_attempts = QuizAttempt.objects.count()
        companies = CompanyTag.objects.annotate(
            question_count=Count('questions')
        )[:8]
        top_users = UserProfile.objects.select_related('user').order_by('-total_xp')[:5]
    except Exception:
        # Tables don't exist yet — redirect to setup
        return redirect('setup')

    context = {
        'categories': categories,
        'total_questions': total_questions,
        'total_users': total_users,
        'total_attempts': total_attempts,
        'companies': companies,
        'top_users': top_users,
    }
    return render(request, 'core/home.html', context)


def setup_view(request):
    """Run migrations and seed data for first-time deployment."""
    from django.core.management import call_command
    from io import StringIO
    output = StringIO()
    try:
        call_command('migrate', '--noinput', stdout=output)
        migrate_output = output.getvalue()
    except Exception as e:
        migrate_output = f"Migration error: {e}"

    seed_output = ""
    try:
        seed_out = StringIO()
        call_command('seed_data', stdout=seed_out)
        seed_output = seed_out.getvalue()
    except Exception as e:
        seed_output = f"Seed skipped: {e}"

    html = f"""
    <html><head><title>AptiTrack Setup</title>
    <style>body{{background:#030303;color:#fff;font-family:monospace;padding:40px;}}
    pre{{background:#111;padding:20px;border-radius:8px;overflow:auto;}}
    a{{color:#8b5cf6;font-size:18px;}}</style></head>
    <body>
    <h1>⚡ AptiTrack Setup Complete</h1>
    <h3>Migration Output:</h3><pre>{migrate_output}</pre>
    <h3>Seed Data Output:</h3><pre>{seed_output}</pre>
    <br><a href="/">→ Go to Homepage</a>
    </body></html>
    """
    from django.http import HttpResponse
    return HttpResponse(html)


# ─── Authentication ───────────────────────────────────────────

def signup_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to AptiTrack, {user.username}! 🎉')
            return redirect('dashboard')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Update streak on login
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.update_streak()
            messages.success(request, f'Welcome back, {user.username}! 🔥')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile page with stats."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            profile.bio = form.cleaned_data['bio']
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'bio': profile.bio,
        })

    # Stats
    attempts = QuizAttempt.objects.filter(user=request.user)
    total_attempted = attempts.aggregate(total=Sum('total_questions'))['total'] or 0
    total_correct = attempts.aggregate(total=Sum('score'))['total'] or 0
    accuracy = round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0
    total_time = attempts.aggregate(total=Sum('time_taken_seconds'))['total'] or 0
    recent_attempts = attempts[:5]

    context = {
        'profile': profile,
        'form': form,
        'total_attempted': total_attempted,
        'total_correct': total_correct,
        'accuracy': accuracy,
        'total_time': total_time,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'core/profile.html', context)


# ─── Dashboard ────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """Performance dashboard with analytics."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.update_streak()

    attempts = QuizAttempt.objects.filter(user=request.user)
    user_answers = UserAnswer.objects.filter(attempt__user=request.user)

    # Overall stats
    total_attempted = user_answers.count()
    total_correct = user_answers.filter(is_correct=True).count()
    accuracy = round((total_correct / total_attempted * 100), 1) if total_attempted > 0 else 0
    total_time = attempts.aggregate(total=Sum('time_taken_seconds'))['total'] or 0
    total_quizzes = attempts.count()

    # Category-wise performance for radar chart
    categories = Category.objects.all()
    category_stats = []
    for cat in categories:
        cat_answers = user_answers.filter(question__category=cat)
        cat_total = cat_answers.count()
        cat_correct = cat_answers.filter(is_correct=True).count()
        cat_accuracy = round((cat_correct / cat_total * 100), 1) if cat_total > 0 else 0
        category_stats.append({
            'name': cat.name,
            'slug': cat.slug,
            'color': cat.color,
            'icon': cat.icon,
            'total': cat_total,
            'correct': cat_correct,
            'accuracy': cat_accuracy,
        })

    # Difficulty breakdown for bar chart
    difficulty_stats = []
    for diff_val, diff_label in Question.DIFFICULTY_CHOICES:
        diff_answers = user_answers.filter(question__difficulty=diff_val)
        diff_total = diff_answers.count()
        diff_correct = diff_answers.filter(is_correct=True).count()
        diff_accuracy = round((diff_correct / diff_total * 100), 1) if diff_total > 0 else 0
        difficulty_stats.append({
            'level': diff_label,
            'total': diff_total,
            'correct': diff_correct,
            'accuracy': diff_accuracy,
        })

    # Recent activity (last 7 attempts) for line chart
    recent_attempts = attempts.order_by('-started_at')[:10]
    activity_data = []
    for attempt in reversed(list(recent_attempts)):
        activity_data.append({
            'date': attempt.started_at.strftime('%b %d'),
            'accuracy': attempt.accuracy,
            'score': attempt.score,
        })

    # Weak topics (< 50% accuracy with at least 5 attempts)
    weak_topics = [cs for cs in category_stats if cs['total'] >= 5 and cs['accuracy'] < 50]
    strong_topics = [cs for cs in category_stats if cs['total'] >= 5 and cs['accuracy'] >= 70]

    # Recommendations
    recommendations = []
    for weak in weak_topics:
        recommendations.append(f"Practice more {weak['name']} — your accuracy is {weak['accuracy']}%")
    if not recommendations and total_attempted < 20:
        recommendations.append("Try attempting more questions to get personalized recommendations!")
    if profile.streak_count == 0:
        recommendations.append("Start a daily streak by practicing every day!")

    context = {
        'profile': profile,
        'total_attempted': total_attempted,
        'total_correct': total_correct,
        'accuracy': accuracy,
        'total_time': total_time,
        'total_quizzes': total_quizzes,
        'category_stats': category_stats,
        'category_stats_json': json.dumps(category_stats),
        'difficulty_stats': difficulty_stats,
        'difficulty_stats_json': json.dumps(difficulty_stats),
        'activity_data_json': json.dumps(activity_data),
        'weak_topics': weak_topics,
        'strong_topics': strong_topics,
        'recommendations': recommendations,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'core/dashboard.html', context)


# ─── Practice Mode ────────────────────────────────────────────

def practice_view(request):
    """Topic-wise practice with filters."""
    questions = Question.objects.select_related('category').prefetch_related('companies')

    # Filters
    category_slug = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    company_slug = request.GET.get('company', '')
    search = request.GET.get('search', '')

    active_category = None
    active_company = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        questions = questions.filter(category=active_category)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if company_slug:
        active_company = get_object_or_404(CompanyTag, slug=company_slug)
        questions = questions.filter(companies=active_company)
    if search:
        questions = questions.filter(text__icontains=search)

    # Get user bookmarks for bookmark status
    bookmarked_ids = []
    if request.user.is_authenticated:
        bookmarked_ids = list(
            Bookmark.objects.filter(user=request.user).values_list('question_id', flat=True)
        )

    paginator = Paginator(questions, 20)
    page = request.GET.get('page', 1)
    questions_page = paginator.get_page(page)

    all_companies = CompanyTag.objects.annotate(question_count=Count('questions'))

    context = {
        'questions': questions_page,
        'active_category': active_category,
        'active_company': active_company,
        'active_difficulty': difficulty,
        'search_query': search,
        'bookmarked_ids': bookmarked_ids,
        'all_companies': all_companies,
        'total_results': paginator.count,
    }
    return render(request, 'core/practice.html', context)


def question_detail_view(request, pk):
    """Single question view with answer reveal."""
    question = get_object_or_404(
        Question.objects.select_related('category').prefetch_related('companies'),
        pk=pk
    )

    is_bookmarked = False
    user_previous_answer = None
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, question=question).exists()
        # Get user's last answer to this question
        last_answer = UserAnswer.objects.filter(
            attempt__user=request.user, question=question
        ).order_by('-attempt__started_at').first()
        if last_answer:
            user_previous_answer = last_answer

    # Handle practice answer submission
    if request.method == 'POST' and request.user.is_authenticated:
        selected = request.POST.get('answer', '')
        if selected in ['a', 'b', 'c', 'd']:
            is_correct = (selected == question.correct_answer)

            # Update question stats
            question.times_attempted += 1
            if is_correct:
                question.times_correct += 1
            question.save()

            # Create practice attempt
            attempt = QuizAttempt.objects.create(
                user=request.user,
                category=question.category,
                score=1 if is_correct else 0,
                total_questions=1,
                time_taken_seconds=int(request.POST.get('time_spent', 0)),
                is_practice=True,
                finished_at=timezone.now(),
                xp_earned=question.xp_value if is_correct else 0,
            )
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=selected,
                is_correct=is_correct,
                time_spent_seconds=int(request.POST.get('time_spent', 0)),
            )

            # Update XP
            if is_correct:
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.add_xp(question.xp_value)
                profile.update_streak()

            return JsonResponse({
                'correct': is_correct,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'xp': question.xp_value if is_correct else 0,
            })

    # Related questions
    related = Question.objects.filter(
        category=question.category
    ).exclude(pk=question.pk).order_by('?')[:5]

    context = {
        'question': question,
        'is_bookmarked': is_bookmarked,
        'user_previous_answer': user_previous_answer,
        'related_questions': related,
    }
    return render(request, 'core/question_detail.html', context)


# ─── Quiz Engine ──────────────────────────────────────────────

@login_required
def quiz_start_view(request):
    """Quiz configuration page."""
    if request.method == 'POST':
        form = QuizConfigForm(request.POST)
        if form.is_valid():
            # Build question queryset
            questions = Question.objects.all()

            category_slug = form.cleaned_data.get('category')
            company_slug = form.cleaned_data.get('company')
            difficulty = form.cleaned_data.get('difficulty')
            num_questions = int(form.cleaned_data['num_questions'])
            time_limit = int(form.cleaned_data['time_limit'])

            if category_slug:
                questions = questions.filter(category__slug=category_slug)
            if company_slug:
                questions = questions.filter(companies__slug=company_slug)
            if difficulty:
                questions = questions.filter(difficulty=difficulty)

            # Random selection
            question_ids = list(questions.values_list('id', flat=True))
            if len(question_ids) < num_questions:
                num_questions = len(question_ids)

            if num_questions == 0:
                messages.warning(request, 'No questions found matching your criteria. Try different filters.')
                return redirect('quiz_start')

            selected_ids = random.sample(question_ids, num_questions)

            # Store in session
            request.session['quiz_question_ids'] = selected_ids
            request.session['quiz_time_limit'] = time_limit
            request.session['quiz_category'] = category_slug or ''
            request.session['quiz_company'] = company_slug or ''
            request.session['quiz_started'] = timezone.now().isoformat()

            return redirect('quiz_play')
    else:
        initial = {}
        if request.GET.get('category'):
            initial['category'] = request.GET['category']
        if request.GET.get('company'):
            initial['company'] = request.GET['company']
        form = QuizConfigForm(initial=initial)

    categories = Category.objects.annotate(question_count=Count('questions'))
    companies = CompanyTag.objects.annotate(question_count=Count('questions'))

    context = {
        'form': form,
        'categories': categories,
        'companies': companies,
    }
    return render(request, 'core/quiz_start.html', context)


@login_required
def quiz_play_view(request):
    """Active quiz with timer."""
    question_ids = request.session.get('quiz_question_ids', [])
    time_limit = request.session.get('quiz_time_limit', 30)

    if not question_ids:
        messages.error(request, 'No active quiz. Please start a new quiz.')
        return redirect('quiz_start')

    questions = Question.objects.filter(id__in=question_ids).select_related('category')
    # Maintain order
    id_to_question = {q.id: q for q in questions}
    ordered_questions = [id_to_question[qid] for qid in question_ids if qid in id_to_question]

    context = {
        'questions': ordered_questions,
        'time_limit': time_limit,
        'total_questions': len(ordered_questions),
    }
    return render(request, 'core/quiz_play.html', context)


@login_required
def quiz_submit_view(request):
    """Process quiz submission."""
    if request.method != 'POST':
        return redirect('quiz_start')

    question_ids = request.session.get('quiz_question_ids', [])
    if not question_ids:
        return redirect('quiz_start')

    questions = Question.objects.filter(id__in=question_ids)
    category_slug = request.session.get('quiz_category', '')
    company_slug = request.session.get('quiz_company', '')
    time_taken = int(request.POST.get('time_taken', 0))

    # Determine category
    category = None
    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()

    # Create attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        category=category,
        total_questions=len(question_ids),
        time_taken_seconds=time_taken,
        finished_at=timezone.now(),
    )

    score = 0
    total_xp = 0
    for question in questions:
        selected = request.POST.get(f'question_{question.id}', '')
        if selected not in ['a', 'b', 'c', 'd']:
            selected = ''

        is_correct = (selected == question.correct_answer) if selected else False
        if is_correct:
            score += 1
            total_xp += question.xp_value

        # Update question stats
        question.times_attempted += 1
        if is_correct:
            question.times_correct += 1
        question.save()

        if selected:
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=selected,
                is_correct=is_correct,
            )

    attempt.score = score
    attempt.xp_earned = total_xp
    attempt.save()

    # Update user XP and streak
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.add_xp(total_xp)
    profile.update_streak()

    # Clear session
    for key in ['quiz_question_ids', 'quiz_time_limit', 'quiz_category', 'quiz_company', 'quiz_started']:
        request.session.pop(key, None)

    return redirect('quiz_result', attempt_id=attempt.id)


@login_required
def quiz_result_view(request, attempt_id):
    """Quiz results page."""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    answers = UserAnswer.objects.filter(attempt=attempt).select_related('question', 'question__category')

    # Get all questions in the quiz (including unanswered)
    answered_question_ids = answers.values_list('question_id', flat=True)

    context = {
        'attempt': attempt,
        'answers': answers,
        'correct_count': answers.filter(is_correct=True).count(),
        'wrong_count': answers.filter(is_correct=False).count(),
        'unanswered': attempt.total_questions - answers.count(),
    }
    return render(request, 'core/quiz_result.html', context)


# ─── Bookmarks ────────────────────────────────────────────────

@login_required
def toggle_bookmark(request, question_id):
    """Toggle bookmark on a question (AJAX)."""
    question = get_object_or_404(Question, id=question_id)
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user, question=question
    )

    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False})

    return JsonResponse({'bookmarked': True})


@login_required
def bookmarks_view(request):
    """List all bookmarked questions."""
    bookmarks = Bookmark.objects.filter(
        user=request.user
    ).select_related('question', 'question__category')

    context = {
        'bookmarks': bookmarks,
    }
    return render(request, 'core/bookmarks.html', context)


@login_required
def review_view(request):
    """Review incorrectly answered questions."""
    wrong_answers = UserAnswer.objects.filter(
        attempt__user=request.user,
        is_correct=False,
    ).select_related(
        'question', 'question__category', 'attempt'
    ).order_by('-attempt__started_at')

    # Remove duplicates (keep latest attempt per question)
    seen = set()
    unique_wrong = []
    for answer in wrong_answers:
        if answer.question_id not in seen:
            seen.add(answer.question_id)
            unique_wrong.append(answer)

    paginator = Paginator(unique_wrong, 20)
    page = request.GET.get('page', 1)
    answers_page = paginator.get_page(page)

    context = {
        'wrong_answers': answers_page,
        'total_wrong': len(unique_wrong),
    }
    return render(request, 'core/review.html', context)


# ─── Company Preparation ─────────────────────────────────────

def company_list_view(request):
    """List all companies with question counts."""
    companies = CompanyTag.objects.annotate(
        question_count=Count('questions')
    ).filter(question_count__gt=0)

    context = {
        'companies': companies,
    }
    return render(request, 'core/company_list.html', context)


def company_detail_view(request, slug):
    """Company-specific questions and mock test."""
    company = get_object_or_404(CompanyTag, slug=slug)
    questions = Question.objects.filter(
        companies=company
    ).select_related('category')

    # Stats
    category_breakdown = questions.values(
        'category__name', 'category__color'
    ).annotate(count=Count('id'))
    difficulty_breakdown = questions.values('difficulty').annotate(count=Count('id'))

    paginator = Paginator(questions, 20)
    page = request.GET.get('page', 1)
    questions_page = paginator.get_page(page)

    context = {
        'company': company,
        'questions': questions_page,
        'total_questions': questions.count(),
        'category_breakdown': list(category_breakdown),
        'difficulty_breakdown': list(difficulty_breakdown),
    }
    return render(request, 'core/company_detail.html', context)


# ─── Leaderboard ──────────────────────────────────────────────

def leaderboard_view(request):
    """Global leaderboard ranked by XP."""
    period = request.GET.get('period', 'all')

    profiles = UserProfile.objects.select_related('user').order_by('-total_xp')

    if period == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        # Get users who were active this week
        active_users = QuizAttempt.objects.filter(
            started_at__gte=week_ago
        ).values_list('user_id', flat=True).distinct()
        profiles = profiles.filter(user_id__in=active_users)
    elif period == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        active_users = QuizAttempt.objects.filter(
            started_at__gte=month_ago
        ).values_list('user_id', flat=True).distinct()
        profiles = profiles.filter(user_id__in=active_users)

    # Add rank
    ranked_profiles = []
    for idx, profile in enumerate(profiles[:50], 1):
        attempts = QuizAttempt.objects.filter(user=profile.user)
        total_q = attempts.aggregate(t=Sum('total_questions'))['t'] or 0
        total_c = attempts.aggregate(t=Sum('score'))['t'] or 0
        acc = round((total_c / total_q * 100), 1) if total_q > 0 else 0
        ranked_profiles.append({
            'rank': idx,
            'profile': profile,
            'accuracy': acc,
            'questions_solved': total_q,
        })

    context = {
        'ranked_profiles': ranked_profiles,
        'active_period': period,
    }
    return render(request, 'core/leaderboard.html', context)


# ─── Categories ───────────────────────────────────────────────

def categories_view(request):
    """Browse all categories."""
    cats = Category.objects.annotate(
        question_count=Count('questions'),
        easy_count=Count('questions', filter=Q(questions__difficulty='easy')),
        medium_count=Count('questions', filter=Q(questions__difficulty='medium')),
        hard_count=Count('questions', filter=Q(questions__difficulty='hard')),
    )

    # Add user progress if authenticated
    category_data = []
    for cat in cats:
        data = {
            'category': cat,
            'question_count': cat.question_count,
            'easy_count': cat.easy_count,
            'medium_count': cat.medium_count,
            'hard_count': cat.hard_count,
            'user_attempted': 0,
            'user_correct': 0,
            'user_accuracy': 0,
        }
        if request.user.is_authenticated:
            user_answers = UserAnswer.objects.filter(
                attempt__user=request.user,
                question__category=cat,
            )
            data['user_attempted'] = user_answers.count()
            data['user_correct'] = user_answers.filter(is_correct=True).count()
            if data['user_attempted'] > 0:
                data['user_accuracy'] = round(
                    (data['user_correct'] / data['user_attempted']) * 100, 1
                )
        category_data.append(data)

    context = {
        'category_data': category_data,
    }
    return render(request, 'core/categories.html', context)
