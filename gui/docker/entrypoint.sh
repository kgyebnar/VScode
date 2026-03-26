#!/bin/sh
set -eu

mkdir -p /data/backups /data/logs /run/nginx
rm -f /etc/nginx/sites-enabled/default

cd /app/backend

python -m uvicorn app:app \
  --host "${BACKEND_HOST:-0.0.0.0}" \
  --port "${BACKEND_PORT:-8000}" &

BACKEND_PID="$!"

term_handler() {
  kill -TERM "$BACKEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
  exit 0
}

trap term_handler INT TERM

nginx -g 'daemon off;' &
NGINX_PID="$!"

while true; do
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    wait "$BACKEND_PID" 2>/dev/null || true
    kill -TERM "$NGINX_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    exit 0
  fi

  if ! kill -0 "$NGINX_PID" 2>/dev/null; then
    kill -TERM "$BACKEND_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
    exit 1
  fi

  sleep 1
done
