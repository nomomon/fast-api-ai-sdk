"""Weather tool."""

import json

import httpx
from pydantic import BaseModel, Field

from ai.agent.tools.base import Tool


class GetCurrentWeather(Tool):
    """Get current weather for a location."""

    class Input(BaseModel):
        latitude: float = Field(description="Latitude of the location")
        longitude: float = Field(description="Longitude of the location")

    async def execute(self, input: Input) -> str:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": input.latitude,
            "longitude": input.longitude,
            "current": "temperature_2m",
            "hourly": "temperature_2m",
            "daily": "sunrise,sunset",
            "timezone": "auto",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return json.dumps(response.json())
