"""Abstract base class for agent tools."""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel
from ai.utils.text import camel_to_snake_case


class Tool(ABC):
    """Abstract base class for agent tools.

    Subclasses define parameters via a nested `Input` model, and implement
    `execute` to perform the tool's logic.

    `name` defaults to the snake_case class name; `description` defaults to
    the class docstring. Both can be overridden as class variables.

    Example::

        class GetWeather(Tool):
            \"\"\"Get current weather for a location.\"\"\"

            class Input(BaseModel):
                latitude: float = Field(description="Latitude of the location")
                longitude: float = Field(description="Longitude of the location")

            async def execute(self, input: Input) -> str:
                ...
    """

    name: ClassVar[str]
    description: ClassVar[str]

    class Input(BaseModel):
        """Override to define the tool's input parameters."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "name" not in cls.__dict__:
            cls.name = camel_to_snake_case(cls.__name__)
        if "description" not in cls.__dict__:
            cls.description = inspect.getdoc(cls) or ""

    @abstractmethod
    async def execute(self, input: Any) -> str:
        """Execute the tool with validated input."""

    async def call(self, args: dict[str, Any]) -> str:
        """Validate `args` against `Input` and call `execute`."""
        return await self.execute(self.Input.model_validate(args))

    def to_schema(self) -> dict[str, Any]:
        """Return an OpenAI function-calling tool schema."""
        schema = self.Input.model_json_schema()
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                },
            },
        }
