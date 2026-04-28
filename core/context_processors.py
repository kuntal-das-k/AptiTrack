"""
Global template context processors for AptiTrack.
"""


def global_context(request):
    """Add global data to all templates."""
    try:
        from .models import Category
        categories = Category.objects.all()
    except Exception:
        categories = []
    return {
        'categories': categories,
        'app_name': 'AptiTrack',
    }
