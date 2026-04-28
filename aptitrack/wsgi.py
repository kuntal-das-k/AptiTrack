"""
WSGI config for AptiTrack project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aptitrack.settings')
application = get_wsgi_application()

# Auto-run migrations on serverless cold start (Vercel)
if os.environ.get('DATABASE_URL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput')
    except Exception as e:
        print(f"Auto-migrate skipped: {e}")

app = application
