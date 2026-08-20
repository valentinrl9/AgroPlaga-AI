#!/usr/bin/env bash
# Deploy NEXO Field Pro V2.0 en VPS piloto (agroplaga-ai.farm)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="deploy/pilot.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Falta $ENV_FILE — cp deploy/pilot.env.example deploy/pilot.env y rellena secretos."
  exit 1
fi

echo "=== V2.0 deploy — $(date -Iseconds) ==="
echo "=== pilot.env (dominio) ==="
grep -E '^(API_DOMAIN|ENVIRONMENT|DOCS_ENABLED|DEMO_SEED_USERS)=' "$ENV_FILE" || true

echo "=== backup PostgreSQL ==="
docker exec -t agroplaga-db-1 pg_dump -U plagaia plagaia_db > ~/backup_pre_v2_$(date +%Y%m%d_%H%M).sql
ls -lh ~/backup_pre_v2_*.sql | tail -1

echo "=== git nexoagro ==="
git fetch origin nexoagro
git checkout nexoagro
git pull origin nexoagro

echo "=== build panel B2B ==="
if command -v npm >/dev/null 2>&1; then
  bash deploy/build-panel.sh
elif [[ -f web-panel/dist/index.html ]]; then
  echo "npm no instalado — usando web-panel/dist del repo (OK para piloto)."
else
  echo "npm no encontrado y falta web-panel/dist/index.html"
  echo "  En tu PC: cd web-panel && npm ci && npm run build"
  echo "  Luego: git add web-panel/dist && git push  (o scp dist al VPS)"
  exit 1
fi

echo "=== docker compose up (migraciones 0021-0023) ==="
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga up -d --build

echo "=== esperar backend ==="
sleep 15

echo "=== alembic head ==="
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga exec -T backend alembic current

echo "=== refresh SIGPAC centroids ==="
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga exec -T backend python scripts/refresh_sigpac_centroids.py

API_DOMAIN="$(grep '^API_DOMAIN=' "$ENV_FILE" | cut -d= -f2-)"
echo "=== smoke HTTP ==="
curl -sI "https://${API_DOMAIN}/api/v1/climate/health" | head -n 1
curl -sI "https://${API_DOMAIN}/panel/" | head -n 1

echo ""
echo "=== V2 desplegado ==="
echo "APK (compilar en PC):"
echo "  cd frontend && flutter build apk --release --dart-define=API_BASE_URL=https://${API_DOMAIN}"
echo "Smoke API: python backend/scripts/smoke_test_nexo.py"
