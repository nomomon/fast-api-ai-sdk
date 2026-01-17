from collections.abc import Sequence

from google import genai
from google.genai import types

from app.config import settings
from app.providers.base import BaseProvider
from app.utils.prompt import ClientMessage


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None):
        self.client = genai.Client(api_key=api_key or settings.gemini_api_key)
        self.model = "gemini-3-flash-preview"

    def convert_to_google_messages(
        self, messages: Sequence[ClientMessage]
    ) -> tuple[list[types.Content], str | None]:
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
                    texts = [p.text for p in msg.parts if p.type == "text" and p.text]
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
                    if part.type == "text" and part.text:
                        parts.append(types.Part(text=part.text))

            if parts:
                google_messages.append(types.Content(role=role, parts=parts))

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
        text_finished = False
        reasoning_stream_id = "reasoning-1"
        reasoning_started = False
        reasoning_finished = False

        yield self.format_sse({"type": "start", "messageId": message_id})

        google_contents, system_instruction = self.convert_to_google_messages(messages)

        # Build config with thinking enabled
        config_params = {}
        if system_instruction:
            config_params["system_instruction"] = system_instruction

        # Add thinking config for reasoning support
        config_params["thinking_config"] = types.ThinkingConfig(include_thoughts=True)

        config = types.GenerateContentConfig(**config_params)

        try:
            # We need to reconstruct the chat history if we act as a stateless endpoint
            # generate_content with a list of contents acts as a chat

            response_stream = self.client.models.generate_content_stream(
                model=model, contents=google_contents, config=config
            )

            for chunk in response_stream:
                # Handle reasoning and text parts separately
                if hasattr(chunk, "candidates") and chunk.candidates:
                    candidate = chunk.candidates[0]
                    if (
                        hasattr(candidate, "content")
                        and candidate.content
                        and candidate.content.parts
                    ):
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                # Check if this is a thought (reasoning) or regular text
                                if hasattr(part, "thought") and part.thought:
                                    # This is reasoning content
                                    if not reasoning_started:
                                        yield self.format_sse(
                                            {"type": "reasoning-start", "id": reasoning_stream_id}
                                        )
                                        reasoning_started = True
                                    yield self.format_sse(
                                        {
                                            "type": "reasoning-delta",
                                            "id": reasoning_stream_id,
                                            "delta": part.text,
                                        }
                                    )
                                else:
                                    # This is regular text content
                                    if not text_started:
                                        yield self.format_sse(
                                            {"type": "text-start", "id": text_stream_id}
                                        )
                                        text_started = True
                                    yield self.format_sse(
                                        {
                                            "type": "text-delta",
                                            "id": text_stream_id,
                                            "delta": part.text,
                                        }
                                    )

                # Fallback to the original text property for backwards compatibility
                elif hasattr(chunk, "text") and chunk.text:
                    if not text_started:
                        yield self.format_sse({"type": "text-start", "id": text_stream_id})
                        text_started = True
                    yield self.format_sse(
                        {"type": "text-delta", "id": text_stream_id, "delta": chunk.text}
                    )

            # Finish reasoning stream if it was started
            if reasoning_started and not reasoning_finished:
                yield self.format_sse({"type": "reasoning-end", "id": reasoning_stream_id})
                reasoning_finished = True

            # Finish text stream if it was started
            if text_started and not text_finished:
                yield self.format_sse({"type": "text-end", "id": text_stream_id})
                text_finished = True

            # Finish
            # Simplified finish reason
            yield self.format_sse({"type": "finish", "finishReason": "stop"})

        except Exception as e:
            print(f"Error in GeminiProvider stream_chat: {e}")
            yield self.format_sse({"type": "error", "text": str(e)})
