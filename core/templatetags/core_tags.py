"""
Custom template tags and filters for AptiTrack.
"""
from django import template

register = template.Library()


@register.filter
def percentage(value, total):
    """Calculate percentage: {{ value|percentage:total }}"""
    try:
        return round((int(value) / int(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def difficulty_badge(difficulty):
    """Return colored badge HTML for difficulty level."""
    colors = {
        'easy': ('#10b981', '#064e3b'),
        'medium': ('#f59e0b', '#78350f'),
        'hard': ('#ef4444', '#7f1d1d'),
    }
    bg, text_color = colors.get(difficulty, ('#6b7280', '#1f2937'))
    return f'<span class="badge" style="background:{bg};color:{text_color}">{difficulty.title()}</span>'


@register.filter
def get_option(question, letter):
    """Get option text by letter: {{ question|get_option:'a' }}"""
    options = {
        'a': question.option_a,
        'b': question.option_b,
        'c': question.option_c,
        'd': question.option_d,
    }
    return options.get(letter, '')


@register.filter
def format_time(seconds):
    """Format seconds to mm:ss."""
    try:
        seconds = int(seconds)
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    except (ValueError, TypeError):
        return "0m 0s"


@register.filter
def subtract(value, arg):
    """Subtract: {{ value|subtract:arg }}"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiply: {{ value|multiply:arg }}"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide: {{ value|divide:arg }}"""
    try:
        return round(float(value) / float(arg), 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
