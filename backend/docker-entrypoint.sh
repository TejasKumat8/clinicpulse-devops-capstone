#!/bin/sh
# Container startup script: wait for PostgreSQL availability, run Alembic migrations, then launch Uvicorn.
set -eu

MAX_ATTEMPTS="${MIGRATION_MAX_ATTEMPTS:-30}"
attempt=1

echo "Starting ClinicPulse backend service..."
until alembic upgrade head; do
  if [ "$attempt" -ge "$MAX_ATTEMPTS" ]; then
    echo "Database still unavailable after ${MAX_ATTEMPTS} attempts, giving up." >&2
    exit 1
  fi
  echo "Database not ready yet (attempt ${attempt}/${MAX_ATTEMPTS}), retrying in 2s..."
  attempt=$((attempt + 1))
  sleep 2
done

echo "Database migrations applied successfully. Launching Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*'
