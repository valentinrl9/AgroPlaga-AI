# AgroPlaga AI

Plataforma de diagnóstico fitosanitario con IA local y red colaborativa comunitaria (mapa de calor, alertas tempranas, zonas SIGPAC).

## Estructura

- `backend/`: FastAPI + PostgreSQL/PostGIS + JWT.
- `frontend/`: Flutter (móvil).
- `docs/`: Guía del proyecto, [ROADMAP.md](docs/ROADMAP.md) y **próximo hito:** [PROXIMO_HITO_V16_CORE.md](docs/PROXIMO_HITO_V16_CORE.md).

## Módulo colaborativo (API)

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/zones` | Catálogo zonas SIGPAC municipio |
| `GET/POST /api/v1/outbreak-events` | Eventos colaborativos anonimizados |
| `PATCH /api/v1/outbreak-events/{id}/validate` | Validación por técnico/admin |
| `GET /api/v1/alerts` | Alertas tempranas por zona |

## Backend (Docker recomendado)

**Desarrollo local (LAN):**

```bash
docker compose up --build
```

La API queda en `http://localhost:8000` y las migraciones + seed SIGPAC se ejecutan al arrancar.

**Piloto 24/7 (VPS + HTTPS):** ver [docs/PILOTO_DESPLIEGUE.md](docs/PILOTO_DESPLIEGUE.md).

```bash
cp deploy/pilot.env.example deploy/pilot.env
# editar deploy/pilot.env
./deploy/setup-pilot.sh
```

Sin Docker:

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload --port 8000
```

Requiere PostgreSQL con extensión PostGIS.

## Frontend

Usa Flutter para ejecutar el proyecto en `frontend/`.
