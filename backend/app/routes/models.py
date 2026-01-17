from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Model(BaseModel):
    id: str
    name: str
    provider: str

@router.get("/models")
async def list_models():
    """List available AI models."""
    return {
        "models": [
            {
                "id": "gpt-5",
                "name": "GPT-5",
                "provider": "OpenAI"
            },
            {
                "id": "gemini-3-flash-preview",
                "name": "Gemini 3 Flash",
                "provider": "Google"
            }
        ]
    }
