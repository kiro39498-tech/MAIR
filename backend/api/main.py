"""
FastAPI entry point. Run with: uvicorn api.main:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from persistence.db import Base, engine

from config.settings import settings
from api.routes import dashboard, copilot, replenishment

def check_and_apply_migrations():
    import sqlite3
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email_send_status FROM replenishment_actions LIMIT 1")
    except sqlite3.OperationalError:
        try:
            cursor.execute("ALTER TABLE replenishment_actions ADD COLUMN email_send_status VARCHAR")
            conn.commit()
            print("Successfully migrated database table: added email_send_status column.")
        except Exception as e:
            print(f"Migration error: {e}")
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import persistence.models  # Ensure models are registered with Base
    Base.metadata.create_all(bind=engine)
    check_and_apply_migrations()
    yield

print("Allowed CORS Origins:", settings.cors_origins)

app = FastAPI(
    title="Material Availability & Inventory Replenishment Agent — API",
    version="0.1.0",
    description="Phase 1: read-only dashboard analytics + draft-only replenishment copilot.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(copilot.router)
app.include_router(replenishment.router)

@app.get("/health")
def health():
    return {"status": "ok"}
