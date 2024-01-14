#!/bin/bash
# Check if in production mode
if [ "$DJANGO_ENV" = "production" ]; then
    # Start Gunicorn with Waitress serving the Django application
     exec waitress-serve --port=8000 annodashboard.wsgi:application
else
    # Start the Django development server
    exec python manage.py runserver 0.0.0.0:8000
fi
