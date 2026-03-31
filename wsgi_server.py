#!/usr/bin/env python
"""
WSGI server runner for Django with dynamic PORT support.
This is the SAFEST way to handle dynamic PORT across all platforms.
Works on Railway, Heroku, Docker, and local development.
"""
import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_project.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

# Get the WSGI application
application = get_wsgi_application()

def run_server():
    """Run Gunicorn server with dynamic PORT."""
    import subprocess
    
    # Get PORT from environment, default to 8000 for local development
    port = os.environ.get('PORT', '8000')
    
    # Validate port is a number
    try:
        port = int(port)
    except ValueError:
        print(f"ERROR: PORT '{os.environ.get('PORT')}' is not a valid number. Using default 8000.")
        port = 8000
    
    # Get number of workers, default to 4
    workers = os.environ.get('WORKERS', '4')
    
    # Print startup info
    print(f"\n{'='*60}")
    print(f"🚀 Starting Django Application")
    print(f"{'='*60}")
    print(f"PORT: {port}")
    print(f"WORKERS: {workers}")
    print(f"DEBUG: {os.environ.get('DEBUG', 'False')}")
    print(f"{'='*60}\n")
    
    # Build gunicorn command
    cmd = [
        'gunicorn',
        'campus_project.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', str(workers),
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
    ]
    
    # Run gunicorn
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped gracefully")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()
