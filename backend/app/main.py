from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import Base, engine
from app.routes import auth, chat, models

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI Chatbot API with FastAPI",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log error but don't crash the app
        # Database tables will be created when connection is available
        import logging
        logging.error(f"Failed to initialize database on startup: {e}")


# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(models.router, prefix="/api", tags=["models"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Chatbot API", "version": settings.api_version}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    This endpoint should work even if database or auth is not configured.
    """
    return {"status": "healthy"}
