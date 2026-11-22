#!/bin/sh
set -e

# If running from root where backend directory exists, change into it
if [ -d "backend" ]; then
  cd backend
fi

echo "[*] Applying database migrations..."
python manage.py migrate --no-input

echo "[*] Seeding default CMS data if not present..."
python seed_data.py || true

echo "[*] Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
