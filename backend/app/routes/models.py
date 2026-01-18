from fastapi import APIRouter

router = APIRouter()


@router.get("/models")
async def list_models():
    """List available AI models."""
    return {
        "models": [
            {"id": "openai/gpt-5", "name": "GPT-5", "provider": "OpenAI"},
            {"id": "openai/responses/gpt-5", "name": "GPT-5 Think", "provider": "OpenAI"},
            {"id": "gemini/gemini-3-flash-preview", "name": "Gemini 3 Flash", "provider": "Google"},
        ]
    }
