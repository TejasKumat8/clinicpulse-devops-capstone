#!/usr/bin/env bash
# Generates traffic against the ClinicPulse API to trigger Horizontal Pod Autoscaler (HPA) scaling.
# Usage: ./scripts/load-test.sh [TARGET_URL] [CONCURRENCY] [DURATION_SECONDS]
set -euo pipefail

TARGET="${1:-http://localhost:3000}"
CONCURRENCY="${2:-12}"
DURATION="${3:-120}"

echo "Starting ClinicPulse HPA Load Test"
echo "Target URL  : ${TARGET}"
echo "Concurrency : ${CONCURRENCY} workers"
echo "Duration    : ${DURATION} seconds"

END_TIME=$((SECONDS + DURATION))

run_worker() {
  while [ $SECONDS -lt $END_TIME ]; do
    curl -s "${TARGET}/api/appointments/stats" > /dev/null || true
    curl -s "${TARGET}/api/doctors" > /dev/null || true
    curl -s "${TARGET}/api/appointments?limit=50" > /dev/null || true
  done
}

echo "Launching load workers..."
for i in $(seq 1 "$CONCURRENCY"); do
  run_worker &
done

echo "Monitoring HPA scaling (Ctrl+C to stop)..."
while [ $SECONDS -lt $END_TIME ]; do
  if command -v kubectl >/dev/null 2>&1; then
    kubectl get hpa,pods -n clinicpulse -l app.kubernetes.io/component=backend 2>/dev/null || true
  fi
  sleep 5
done

wait
echo "Load test finished successfully."
