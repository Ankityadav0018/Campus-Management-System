release: python manage.py migrate
web: gunicorn campus_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120
