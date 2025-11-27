#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_DIR="${SCRIPT_DIR}/desktop"

echo "[run.sh] Launching CMMS Electron desktop app..."

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
