# AgroPlaga AI

Plataforma de diagnóstico fitosanitario con IA local y red colaborativa comunitaria (mapa de calor, alertas tempranas, zonas SIGPAC).

## Estructura

- `backend/`: FastAPI + PostgreSQL/PostGIS + JWT.
- `frontend/`: Flutter (móvil).
- `docs/`: Guía del proyecto y [ROADMAP.md](docs/ROADMAP.md).

## Módulo colaborativo (API)

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/zones` | Catálogo zonas SIGPAC municipio |
| `GET/POST /api/v1/outbreak-events` | Eventos colaborativos anonimizados |
| `PATCH /api/v1/outbreak-events/{id}/validate` | Validación por técnico/admin |
| `GET /api/v1/alerts` | Alertas tempranas por zona |

## Backend (Docker recomendado)

```bash
docker compose up --build
```

La API queda en `http://localhost:8000` y las migraciones + seed SIGPAC se ejecutan al arrancar.

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
