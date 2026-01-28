"""Tool implementations for AI agents."""

import requests


def get_current_weather(latitude, longitude):
    """Get current weather for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location

    Returns:
        Weather data dictionary or None on error
    """
    # Format the URL with proper parameter substitution
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&hourly=temperature_2m&daily=sunrise,sunset&timezone=auto"

    try:
        # Make the API call
        response = requests.get(url)

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    except requests.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Error fetching weather data: {e}")
        return None


AVAILABLE_TOOLS = {
    "get_current_weather": get_current_weather,
}
