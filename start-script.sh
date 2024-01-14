#!/bin/bash

# Start Nginx in the background
nginx &

# Start Gunicorn with Django
# Adjust the number of workers and other settings as necessary
gunicorn annodashboard.wsgi:application --bind 0.0.0.0:8000
