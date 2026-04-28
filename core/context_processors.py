"""
Global template context processors for AptiTrack.
"""
from .models import Category


def global_context(request):
    """Add global data to all templates."""
    return {
        'categories': Category.objects.all(),
        'app_name': 'AptiTrack',
    }
