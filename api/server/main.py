"""
MIST Nexus — Unified API Gateway
Aetherhaven / clawd | Pillar 1: Local-First Architecture

Base: http://localhost:7777/api/v1
Port 7777: Unified API
Port 8080: VoidChat UI (served separately via static mount)

Run:
    uvicorn src.main:app --host 0.0.0.0 --port 7777 --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import system, now, weather, radio, vtuber, command, research
from .db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="MIST Nexus — Unified API",
    description="Aetherhaven local-first gateway. LOCAL FIRST. CLOUD IS A MIRROR.",
    version=os.getenv("MOTHERSHIP_VERSION", "0.1.0"),
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PREFIX = "/api/v1"
app.include_router(system.router,   prefix=PREFIX, tags=["system"])
app.include_router(now.router,      prefix=PREFIX, tags=["now"])
app.include_router(weather.router,  prefix=PREFIX, tags=["weather"])
app.include_router(radio.router,    prefix=PREFIX, tags=["radio"])
app.include_router(vtuber.router,   prefix=PREFIX, tags=["vtuber"])
app.include_router(command.router,  prefix=PREFIX, tags=["command"])
app.include_router(research.router, prefix=PREFIX, tags=["research"])


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "MIST Nexus",
        "version": app.version,
        "api": "/api/v1",
        "docs": "/api/docs",
        "status": "/api/v1/ecosystem/status",
        "local_first": True,
        "sigil": "✧⟁∅↺⇢≡~∴",
    }
