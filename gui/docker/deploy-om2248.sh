#!/bin/sh
set -eu

IMAGE_NAME="${IMAGE_NAME:-palo-alto-upgrade-gui:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-palo-alto-gui}"
HOST_PORT="${HOST_PORT:-8080}"
CONTAINER_PORT="${CONTAINER_PORT:-80}"
DATA_DIR="${DATA_DIR:-/home/gyebi/palo-alto-gui-data}"
DOCKER_CMD="${DOCKER_CMD:-sudo docker}"
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

printf 'Building image: %s\n' "$IMAGE_NAME"
cd "$ROOT_DIR"
$DOCKER_CMD build -f gui/docker/Dockerfile -t "$IMAGE_NAME" .

printf 'Restarting container: %s\n' "$CONTAINER_NAME"
$DOCKER_CMD rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
$DOCKER_CMD run -d \
  --name "$CONTAINER_NAME" \
  -p "${HOST_PORT}:${CONTAINER_PORT}" \
  -v "${DATA_DIR}:/data" \
  "$IMAGE_NAME" >/dev/null

printf 'Waiting for health check...\n'
health="starting"
attempt=0
while [ "$attempt" -lt 20 ]; do
  health="$($DOCKER_CMD inspect --format '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo starting)"
  printf '  attempt %s: %s\n' "$((attempt + 1))" "$health"
  [ "$health" = "healthy" ] && break
  attempt=$((attempt + 1))
  sleep 2
done

if [ "$health" != "healthy" ]; then
  printf 'Container did not become healthy. Recent logs:\n' >&2
  $DOCKER_CMD logs --tail 80 "$CONTAINER_NAME" >&2 || true
  exit 1
fi

printf '\nGUI is ready:\n'
printf '  http://127.0.0.1:%s\n' "$HOST_PORT"
printf '  http://<vm-ip>:%s\n' "$HOST_PORT"
