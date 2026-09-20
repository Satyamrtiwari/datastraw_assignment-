import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Ensure both backend dir and project root are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
for p in (BACKEND_DIR, PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.database import engine, Base
    from backend.app.routers import tickets, analytics, webhooks
except ImportError:
    from app.database import engine, Base
    from app.routers import tickets, analytics, webhooks


def auto_migrate_schema():
    """Ensure newly added columns exist in the SQLite database."""
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(tickets)"))
            existing_cols = {row[1] for row in result.fetchall()}
            if existing_cols:
                if "priority" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN priority VARCHAR(50) DEFAULT 'Normal' NOT NULL"))
                if "category" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN category VARCHAR(100) DEFAULT 'General' NOT NULL"))
                if "channel" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN channel VARCHAR(50) DEFAULT 'Web Form' NOT NULL"))
                if "client_name" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN client_name VARCHAR(100) DEFAULT 'Aura D2C' NOT NULL"))
                if "ai_summary" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN ai_summary TEXT"))
                conn.commit()
        except Exception as e:
            print(f"Migration check note: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables & columns exist on startup."""
    auto_migrate_schema()
    yield


app = FastAPI(
    title="Datastraw Customer Support CRM API",
    description="Full-stack AI CRM backend with automated triage, suggested drafts, D2C context, and multi-tenancy.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware for local development & deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(tickets.router)
app.include_router(analytics.router)
app.include_router(webhooks.router)


from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DIST_ASSETS = os.path.join(DIST_DIR, "assets")

if os.path.exists(DIST_ASSETS):
    app.mount("/assets", StaticFiles(directory=DIST_ASSETS), name="assets")


@app.get("/", tags=["Health & Web App"])
async def root(request: Request):
    accept = request.headers.get("accept", "")
    dist_index = os.path.join(DIST_DIR, "index.html")
    index_file = dist_index if os.path.exists(dist_index) else os.path.join(FRONTEND_DIR, "index.html")

    # If accessed from browser (text/html), serve the React dashboard!
    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)

    # API JSON response for API clients & tests
    return {
        "service": "Datastraw Support CRM API",
        "status": "online",
        "version": "2.0.0",
        "docs_url": "/docs",
        "features": [
            "Core Ticket CRUD",
            "Multi-channel Ingestion (Email, WhatsApp, Web, Shopify)",
            "Multi-tenant Client/Brand Filtering",
            "AI Ticket Triage & Urgency Classifier",
            "1-Click AI Agent Draft Generator",
            "Simulated D2C Order Context",
            "Support Operations Analytics & KPIs",
        ],
    }


@app.get("/styles.css", include_in_schema=False)
async def get_styles():
    css_file = os.path.join(FRONTEND_DIR, "styles.css")
    if os.path.exists(css_file):
        return FileResponse(css_file, media_type="text/css")
    return JSONResponse(status_code=404, content={"detail": "styles.css not found"})


@app.get("/app.js", include_in_schema=False)
async def get_script():
    js_file = os.path.join(FRONTEND_DIR, "app.js")
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    return JSONResponse(status_code=404, content={"detail": "app.js not found"})


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
