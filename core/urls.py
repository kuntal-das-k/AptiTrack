"""
AptiTrack URL Configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    # Landing
    path('', views.home_view, name='home'),
    path('setup/', views.setup_view, name='setup'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Categories
    path('categories/', views.categories_view, name='categories'),

    # Practice
    path('practice/', views.practice_view, name='practice'),
    path('question/<int:pk>/', views.question_detail_view, name='question_detail'),

    # Quiz
    path('quiz/', views.quiz_start_view, name='quiz_start'),
    path('quiz/play/', views.quiz_play_view, name='quiz_play'),
    path('quiz/submit/', views.quiz_submit_view, name='quiz_submit'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result_view, name='quiz_result'),

    # Bookmarks & Review
    path('bookmark/<int:question_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('review/', views.review_view, name='review'),

    # Company
    path('companies/', views.company_list_view, name='company_list'),
    path('company/<slug:slug>/', views.company_detail_view, name='company_detail'),

    # Leaderboard
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
