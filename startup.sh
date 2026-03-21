#!/bin/bash

echo "=== Startup: $(date) ==="
echo "=== Working dir: $(pwd) ==="
echo "=== SITE_MODE: ${SITE_MODE:-springfield} ==="

# Activate Oryx-built virtual environment if present
if [ -d "/antenv" ]; then
    echo "=== Activating /antenv ==="
    source /antenv/bin/activate
fi

export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

echo "=== Running migrations (60s timeout) ==="
timeout 60 python manage.py migrate --no-input 2>&1 || echo "WARNING: migrate failed or timed out — starting gunicorn anyway"

if [ "${SITE_MODE}" = "construction" ]; then
    echo "=== CONSTRUCTION MODE: seeding STL conversion data ==="
    timeout 30 python manage.py seed_stl_conversions 2>&1 || echo "WARNING: seed_stl_conversions failed (may already exist)"
else
    echo "=== SPRINGFIELD MODE: seeding Springfield data ==="
    timeout 30 python manage.py seed_event_sources 2>&1 || echo "WARNING: seed_event_sources failed"
    timeout 30 python manage.py populate_states 2>&1 || echo "WARNING: populate_states failed"
    timeout 30 python manage.py populate_springfields 2>&1 || echo "WARNING: populate_springfields failed"
fi

echo "=== Starting Gunicorn ==="
exec gunicorn \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --bind 0.0.0.0:8000 \
  --access-logfile '-' \
  --error-logfile '-' \
  mocon.wsgi:application
