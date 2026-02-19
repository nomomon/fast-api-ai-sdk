"""Get current weather tool."""

import requests


def get_current_weather(latitude: float, longitude: float) -> dict | None:
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location

    Returns:
        Weather data dictionary or None on error
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&hourly=temperature_2m&daily=sunrise,sunset&timezone=auto"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
