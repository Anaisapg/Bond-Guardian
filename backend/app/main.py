from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import Database
from app.routers import auth, contacts, interactions, reminders, ritual, chat, photos, settings as settings_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting Bond Guardian API...")
    await Database.connect()

    if Database.is_mock:
        logger.warning("Running in MOCK mode - API will return demo data")
    else:
        logger.info("Database connected successfully!")

    yield

    # Shutdown
    logger.info("Shutting down Bond Guardian API...")
    await Database.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API para Bond Guardian - Tu compañero para cuidar relaciones personales",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:8081",
        "http://localhost:19006",
        "exp://localhost:8081",
        "*",  # Allow all for development - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["Interactions"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])
app.include_router(ritual.router, prefix="/api/ritual", tags=["Ritual"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "¡Bienvenido a Bond Guardian API!",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "mock" if Database.is_mock else "connected",
        "mock_mode": Database.is_mock,
    }
