#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="deploy/pilot.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "No existe $ENV_FILE"
  echo "Copia deploy/pilot.env.example → deploy/pilot.env y edítalo."
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

if [[ -z "${API_DOMAIN:-}" ]] || [[ "$API_DOMAIN" == "api.tudominio.com" ]]; then
  echo "Configura API_DOMAIN en deploy/pilot.env (dominio real apuntando al VPS)."
  exit 1
fi

if [[ "${POSTGRES_PASSWORD:-}" == "cambiar-por-secreto-largo" ]] || [[ "${SECRET_KEY:-}" == cambiar-por-secreto-largo-minimo-32-caracteres ]]; then
  echo "Cambia POSTGRES_PASSWORD y SECRET_KEY en deploy/pilot.env antes de desplegar."
  exit 1
fi

if [[ ! -d web-panel/dist ]] || [[ ! -f web-panel/dist/index.html ]]; then
  echo "Compilando panel web B2B..."
  bash deploy/build-panel.sh
fi

echo "Desplegando piloto en https://${API_DOMAIN} ..."
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" up -d --build

echo ""
echo "Listo. Comprueba:"
echo "  curl -sI https://${API_DOMAIN}/docs | head -n 1"
echo "  curl -sI https://${API_DOMAIN}/panel/ | head -n 1"
echo "  Panel B2B: https://${API_DOMAIN}/panel/"
echo ""
echo "APK (en tu PC con Flutter):"
echo "  cd frontend && flutter build apk --release --dart-define=API_BASE_URL=https://${API_DOMAIN}"
