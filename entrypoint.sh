#!/bin/sh
# -----------------------------------------------
# Container start-up: apply migrations, seed demo data on first boot, start Gunicorn.
# -----------------------------------------------
set -eu

python manage.py migrate --noinput

# Load the demo fixture only on first boot, when no questions exist
python manage.py shell -c "from polls.models import Question; import sys; sys.exit(0 if Question.objects.exists() else 1)" \
    || python manage.py loaddata polls_seed.json

exec gunicorn mysite.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile -
