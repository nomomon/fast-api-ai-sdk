"""Tool definitions (schemas) for LLM function calling."""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather at a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "The latitude of the location",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "The longitude of the location",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        },
    }
]
