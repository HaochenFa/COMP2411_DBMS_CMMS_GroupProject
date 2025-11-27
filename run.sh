#!/usr/bin/env bash
set -euo pipefail

APP_URL="http://localhost:5173"

echo "[run.sh] Starting CMMS stack using Docker Compose..."

if ! command -v docker >/dev/null 2>&1; then
  echo "[run.sh] Error: Docker is not installed or not on PATH."
  echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop and try again."
  exit 1
fi

# Determine whether to use 'docker compose' (v2) or 'docker-compose' (v1)
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "[run.sh] Error: Docker Compose is not available."
  echo "Install Docker Compose or upgrade to Docker Desktop with 'docker compose' support."
  exit 1
fi

# Build and start containers in the background
echo "[run.sh] Running: $COMPOSE_CMD up -d --build"
# shellcheck disable=SC2086
$COMPOSE_CMD up -d --build

echo "[run.sh] Waiting for frontend to become available at ${APP_URL} ..."
READY=0
for i in $(seq 1 30); do
  if command -v curl >/dev/null 2>&1; then
    if curl -sSf "${APP_URL}" >/dev/null 2>&1; then
      READY=1
      break
    fi
  else
    # If curl is not installed, just wait a bit and assume it's fine
    sleep 5
    READY=1
    break
  fi
  sleep 2
done

if [ "$READY" -eq 1 ]; then
  echo "[run.sh] Frontend appears to be up."
else
  echo "[run.sh] Frontend did not become ready within the expected time, but containers are running."
fi

echo "[run.sh] Opening browser at ${APP_URL} ..."
case "$(uname)" in
  Darwin)
    open "${APP_URL}" || echo "[run.sh] Please open ${APP_URL} in your browser."
    ;;
  Linux)
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "${APP_URL}" >/dev/null 2>&1 || echo "[run.sh] Please open ${APP_URL} in your browser."
    else
      echo "[run.sh] Please open ${APP_URL} in your browser."
    fi
    ;;
  *)
    echo "[run.sh] Please open ${APP_URL} in your browser."
    ;;
esac
