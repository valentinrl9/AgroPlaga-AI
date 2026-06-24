#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/web-panel"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm no encontrado. Instala Node.js 18+ o compila en tu PC:"
  echo "  cd web-panel && npm install && npm run build"
  exit 1
fi

npm ci
npm run build
echo "Panel compilado en web-panel/dist"
