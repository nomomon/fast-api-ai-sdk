"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth import router as auth_router
from src.chat import router as chat_router
from src.config import settings
from src.mcp import router as mcp_router
from src.model import router as model_router
from src.prompt import router as prompt_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title="AI Chatbot API",
    version="1.0.0",
    description="AI Chatbot API with FastAPI",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(auth_router)
api.include_router(chat_router)
api.include_router(model_router)
api.include_router(mcp_router)
api.include_router(prompt_router)

app.include_router(api)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AI Chatbot API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
