"""
Global template context processors for AptiTrack.
"""


def global_context(request):
    """Add global data to all templates."""
    try:
        from .models import Category
        nav_categories = Category.objects.all()
    except Exception:
        nav_categories = []
    return {
        'nav_categories': nav_categories,
        'app_name': 'AptiTrack',
    }
