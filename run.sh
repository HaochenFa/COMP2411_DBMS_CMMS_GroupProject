#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="${SCRIPT_DIR}/desktop"

echo "[run.sh] Launching CMMS Electron desktop app..."

# Check that Docker CLI is available
if ! command -v docker >/dev/null 2>&1; then
	echo "[run.sh] Error: Docker CLI (docker) is not installed or not on PATH."
	echo "Please install Docker Desktop (Windows/macOS) or Docker Engine (Linux): https://docs.docker.com/get-docker/"
	exit 1
fi

# Check that the Docker daemon is running and accessible
if ! docker info >/dev/null 2>&1; then
	echo "[run.sh] Error: Docker seems to be installed but the Docker daemon is not running or not accessible."
	echo "Please start Docker Desktop (or your Docker service) and try again."
	exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
	echo "[run.sh] Error: npm (Node.js) is not installed or not on PATH."
	echo "Please install Node.js from https://nodejs.org/ and try again."
	exit 1
fi

if [ ! -d "${DESKTOP_DIR}" ]; then
	echo "[run.sh] Error: desktop directory not found at ${DESKTOP_DIR}."
	exit 1
fi

cd "${DESKTOP_DIR}"

if [ ! -d "node_modules" ]; then
	echo "[run.sh] Installing Electron app dependencies (first-run setup)..."
	npm install
fi

echo "[run.sh] Starting Electron app (npm start)..."
npm start
