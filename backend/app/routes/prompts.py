from fastapi import APIRouter

router = APIRouter(tags=["prompts"])

# Available prompts data
PROMPTS_DATA = [
    {
        "id": "general",
        "name": "General",
        "content": "You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and thoughtful responses to user questions.",
    },
    {
        "id": "goofy",
        "name": "Goofy",
        "content": "You are a fun, playful, and goofy AI assistant with a great sense of humor. While still being helpful, you enjoy adding personality, jokes, and lightheartedness to your responses.",
    },
]


def get_prompt_by_id(prompt_id: str) -> str | None:
    """Get prompt content by ID."""
    for prompt in PROMPTS_DATA:
        if prompt["id"] == prompt_id:
            return prompt["content"]
    return None


@router.get("/prompts")
async def list_prompts():
    """List available system prompts."""
    return {"prompts": PROMPTS_DATA}
