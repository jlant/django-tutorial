#!/bin/sh

# -----------------------------------------------
# Script for Docker container to automatically run migrations, seed initial data if the
# database is empty, and start Gunicorn.
# -----------------------------------------------
set -e

mkdir -p /app/data
uv run manage.py migrate --noinput

# Load initial fixture only on first boot when no questions exist
uv run manage.py shell -c "from polls.models import Question; import sys; sys.exit(0 if Question.objects.exists() else 1)" || uv run manage.py loaddata polls_seed.json

exec uv run gunicorn mysite.wsgi:application --bind 0.0.0.0:8000 --workers 3

