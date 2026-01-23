from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import os
import sys

from config import get_settings
from db import init_db
from logger import setup_logger
from exceptions import (
    AppException, 
    app_exception_handler, 
    general_exception_handler
)
from routes import tasks, meta, integrations, hyperplanning

settings = get_settings()
logger = setup_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(f"✅ {settings.app_name} v{settings.app_version} started")
    logger.info(f"📊 Database: {settings.database_url}")
    yield
    logger.info(f"🛑 {settings.app_name} stopped")

# Application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

# Middleware Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware de performance logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} ({process_time:.3f}s)"
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routers
app.include_router(meta.router)
app.include_router(tasks.router)
app.include_router(integrations.router)
app.include_router(hyperplanning.router)

# Determine path to web folder
# If frozen (exe), look in _MEIPASS/web
# If dev, look in ../web
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    web_path = os.path.join(base_path, "web")
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    web_path = os.path.join(base_path, "..", "web")

# Mount static files (Frontend)
# html=True allows serving index.html automatically at /
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="static")
else:
    logger.warning(f"⚠️ Web directory not found at {web_path}")