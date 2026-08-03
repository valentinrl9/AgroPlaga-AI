#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="deploy/pilot.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Falta $ENV_FILE — créalo en el VPS o cópialo con scp desde tu PC."
  exit 1
fi

echo "=== pilot.env ==="
grep -E '^(API_DOMAIN|POSTGRES_USER|POSTGRES_DB|ADMIN_EMAIL)=' "$ENV_FILE"

echo "=== backup ==="
docker exec -t agroplaga-db-1 pg_dump -U plagaia plagaia_db > ~/backup_pre_1b_$(date +%Y%m%d).sql
ls -lh ~/backup_pre_1b_*.sql | tail -1

echo "=== git nexoagro ==="
git stash push -m "vps landing $(date +%F)" || true
git fetch origin nexoagro
git checkout nexoagro
git pull origin nexoagro

echo "=== build panel ==="
bash deploy/build-panel.sh

echo "=== deploy ==="
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga up -d --build

echo "=== verify ==="
curl -sI https://agroplaga-ai.farm/docs | head -n 1
curl -sI https://agroplaga-ai.farm/panel/ | head -n 1
docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga exec -T backend alembic current
