from typing import Sequence, List

from google import genai
from google.genai import types

from app.config import settings
from app.providers.base import BaseProvider
from app.utils.prompt import ClientMessage

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None):
        self.client = genai.Client(api_key=api_key or settings.gemini_api_key)
        self.model = "gemini-3-flash-preview"

    def convert_to_google_messages(self, messages: Sequence[ClientMessage]) -> tuple[List[types.Content], str | None]:
        google_messages = []
        
        # Handle system message by prepending or using config
        system_instruction = None
        
        for msg in messages:
            role = msg.role
            content = msg.content
            
            if role == "system":
                if content:
                    system_instruction = content
                elif msg.parts:
                    texts = [p.text for p in msg.parts if p.type == 'text' and p.text]
                    if texts:
                        system_instruction = "\n".join(texts)
                continue
                
            if role == "assistant":
                role = "model"
                
            parts = []
            if content:
                parts.append(types.Part(text=content))
            elif msg.parts:
                for part in msg.parts:
                    if part.type == 'text' and part.text:
                        parts.append(types.Part(text=part.text))
            
            if parts:
                google_messages.append(types.Content(
                    role=role,
                    parts=parts
                ))
            
        return google_messages, system_instruction

    async def stream_chat(
        self,
        messages: Sequence[ClientMessage],
        model: str,
        protocol: str = "data",
    ):
        message_id = self.generate_id()
        text_stream_id = "text-1"
        text_started = False
        
        yield self.format_sse({"type": "start", "messageId": message_id})
        
        google_contents, system_instruction = self.convert_to_google_messages(messages)
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction
        ) if system_instruction else None

        try:
            # We need to reconstruct the chat history if we act as a stateless endpoint
            # generate_content with a list of contents acts as a chat
            
            response_stream = self.client.models.generate_content_stream(
                model=model,
                contents=google_contents,
                config=config
            )

            for chunk in response_stream:
                text_delta = chunk.text
                
                if text_delta:  
                    if not text_started:
                        yield self.format_sse({"type": "text-start", "id": text_stream_id})
                        text_started = True
                    
                    yield self.format_sse(
                        {"type": "text-delta", "id": text_stream_id, "delta": text_delta}
                    )
            
            # Finish
            yield self.format_sse({"type": "finish", "finishReason": "stop"}) # Simplified finish reason

        except Exception as e:
            print(f"Error in GeminiProvider stream_chat: {e}")
            yield self.format_sse({"type": "error", "text": str(e)})
