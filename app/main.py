from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, organizer, slots, bookings
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Calendar Booking API",
    description="Backend for Telegram Mini App Booking System",
    version="0.1.0"
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(organizer.router, prefix="/api/v1/organizer", tags=["Organizer"])
app.include_router(slots.router, prefix="/api/v1/slots", tags=["Slots"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])

# Настройка CORS
origins = [
    "http://localhost:3000",          # Локальный React
    "http://127.0.0.1:3000",
    "https://*.github.io",            # GitHub Pages
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # На этапе разработки можно оставить *, но в проде лучше конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} | Time: {process_time:.4f}s | Status: {response.status_code}")
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/health", tags=["System"])
async def health_check():
    """Простая проверка работоспособности API"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }
