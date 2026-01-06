#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput --fake-initial

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
