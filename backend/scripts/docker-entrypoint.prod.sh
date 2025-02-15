#!/bin/sh

# Default values for environment variables
# These are not to be used in production
: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"
: "${WORKERS:=1}"
: "${LOG_LEVEL:=debug}"

# Start uvicorn
exec uvicorn app.api:app \
    --host "$HOST" \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level "$LOG_LEVEL" \
    --proxy-headers \
    --forwarded-allow-ips '*'
