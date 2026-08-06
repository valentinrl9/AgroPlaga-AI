#!/usr/bin/env bash
# Despliega landing + backend (formulario contacto) en VPS piloto.
# Ejecutar EN EL VPS: bash deploy/deploy-landing-contact.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="deploy/pilot.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Falta $ENV_FILE"
  exit 1
fi

# Añadir vars SMTP si no existen (editar SMTP_PASSWORD a mano)
grep -q '^CONTACT_NOTIFY_EMAIL=' "$ENV_FILE" || cat >> "$ENV_FILE" <<'EOF'

# Formulario contacto landing
CONTACT_NOTIFY_EMAIL=valentinruizleon@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=valentinruizleon@gmail.com
SMTP_PASSWORD=
SMTP_FROM=AgroPlaga Piloto <valentinruizleon@gmail.com>
SMTP_USE_TLS=true
EOF

git fetch origin nexoagro
git pull origin nexoagro

docker compose -f docker-compose.pilot.yml --env-file "$ENV_FILE" -p agroplaga up -d --build backend

echo "=== Verificación ==="
curl -sI https://agroplaga-ai.farm/ | head -n 1
curl -sI https://agroplaga-ai.farm/assets/mapa-calor-sur-almeria-3d.png | head -n 1
curl -s -o /dev/null -w "POST contact: %{http_code}\n" -X POST https://agroplaga-ai.farm/api/v1/contact \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test","email":"test@example.com","role":"agricultor","organization":"Test","phone":"+34600000000","interest":"mapa"}'

echo "Landing: https://agroplaga-ai.farm/ (Ctrl+F5)"
echo "Recuerda: pon SMTP_PASSWORD en deploy/pilot.env y vuelve a levantar backend si falta."
