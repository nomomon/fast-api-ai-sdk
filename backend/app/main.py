from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, chat, models, prompts
from app.core import Base, engine, settings
import app.domain # TODO: begin using migrations (e.g., Alembic) for database schema management

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Initialize the database
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup actions on shutdown
    pass


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI Chatbot API with FastAPI",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(chat.router)
api.include_router(models.router)
api.include_router(prompts.router)

app.include_router(api)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Chatbot API", "version": settings.api_version}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
