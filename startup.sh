#!/bin/bash

echo "=== Startup: $(date) ==="
echo "=== Working dir: $(pwd) ==="
echo "=== SITE_MODE: ${SITE_MODE:-springfield} ==="

# Azure App Service stores packages in one of two locations depending on deploy method:
# 1. /antenv              — Oryx/zipdeploy with SCM_DO_BUILD_DURING_DEPLOYMENT=true
# 2. .python_packages     — GitHub Actions workflow deploy (most common)
if [ -d "/antenv" ]; then
    echo "=== Activating /antenv ==="
    source /antenv/bin/activate
fi

if [ -d "/home/site/wwwroot/.python_packages" ]; then
    echo "=== Adding .python_packages to PYTHONPATH ==="
    export PYTHONPATH=/home/site/wwwroot/.python_packages/lib/site-packages:$PYTHONPATH
fi

export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Verify Django is importable before proceeding
python -c "import django; print('=== Django', django.__version__, 'ready ===')" || {
    echo "FATAL: Django not importable — aborting startup"
    exit 1
}

echo "=== Running migrations (60s timeout) ==="
timeout 60 python manage.py migrate --no-input 2>&1 || echo "WARNING: migrate failed or timed out — starting gunicorn anyway"

echo "=== Setting django_site domain for allauth OAuth callbacks ==="
timeout 15 python manage.py shell -c "
import os
from django.contrib.sites.models import Site
domain = os.environ.get('SITE_DOMAIN', 'missouriconstruction.com')
site, created = Site.objects.update_or_create(id=1, defaults={'domain': domain, 'name': domain})
print(f'Site domain set to: {domain} (created={created})')
" 2>&1 || echo "WARNING: could not update Sites table"

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
exec python -m gunicorn \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --bind 0.0.0.0:8000 \
  --access-logfile '-' \
  --error-logfile '-' \
  mocon.wsgi:application
