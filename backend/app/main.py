from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import auth, users, scans, stats, zones, outbreak_events, alerts, heatmap, community, feedback, farms, tech_dashboard, analytics, plagues
from app.core.config import settings
from app.db.init_db import init_db
from app.services.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="AgroPlaga AI API", version="0.1.0", redirect_slashes=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- OpenAPI Auth config ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])
app.include_router(zones.router, prefix="/api/v1/zones", tags=["zones"])
app.include_router(outbreak_events.router, prefix="/api/v1/outbreak-events", tags=["outbreak-events"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(heatmap.router, prefix="/api/v1/heatmap", tags=["heatmap"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(community.router, prefix="/api/v1/community", tags=["community"])
app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(farms.router, prefix="/api/v1/farms", tags=["farms"])
app.include_router(tech_dashboard.router, prefix="/api/v1/tech", tags=["tech-dashboard"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(plagues.router, prefix="/api/v1/plagues", tags=["plagues"])
