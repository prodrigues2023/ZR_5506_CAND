#!/bin/sh
set -eu

echo "Waiting for PostgreSQL..."
until /app/backend/.venv/bin/python /app/db_wait.py 2>/dev/null
do
  sleep 1
done

echo "Applying database migrations..."
cd /app/backend
/app/backend/.venv/bin/python -m alembic upgrade head

echo "Starting application services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/series-atlas.conf
