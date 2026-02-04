"""Tests for tool registry and schema extraction."""

import unittest
from unittest.mock import Mock, patch

from app.services.ai.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS
from app.services.ai.tools.schema import function_to_openai_tool


def _sample_tool(lat: float, lon: float) -> str:
    """Get weather at a place.

    Args:
        lat: Latitude of the location
        lon: Longitude of the location

    Returns:
        A string.
    """
    return f"{lat},{lon}"


class TestSchemaExtractor(unittest.TestCase):
    """Tests for function_to_openai_tool."""

    def test_returns_openai_format(self) -> None:
        """Result has type, function.name, function.description, function.parameters."""
        result = function_to_openai_tool("_sample_tool", _sample_tool)
        self.assertEqual(result["type"], "function")
        self.assertIn("function", result)
        fn = result["function"]
        self.assertEqual(fn["name"], "_sample_tool")
        self.assertIn("description", fn)
        self.assertIn("parameters", fn)
        self.assertEqual(fn["parameters"]["type"], "object")
        self.assertIn("properties", fn["parameters"])
        self.assertIn("required", fn["parameters"])

    def test_parameter_schema_from_type_hints(self) -> None:
        """Parameters get correct JSON Schema types from annotations."""
        result = function_to_openai_tool("_sample_tool", _sample_tool)
        props = result["function"]["parameters"]["properties"]
        self.assertEqual(props["lat"]["type"], "number")
        self.assertEqual(props["lon"]["type"], "number")
        self.assertEqual(props["lat"]["description"], "Latitude of the location")
        self.assertEqual(props["lon"]["description"], "Longitude of the location")
        self.assertCountEqual(result["function"]["parameters"]["required"], ["lat", "lon"])


class TestRegistry(unittest.TestCase):
    """Tests for TOOL_DEFINITIONS and AVAILABLE_TOOLS."""

    def test_registry_exports_get_current_weather(self) -> None:
        """Registry includes get_current_weather in definitions and implementations."""
        names = [d["function"]["name"] for d in TOOL_DEFINITIONS]
        self.assertIn("get_current_weather", names)
        self.assertIn("get_current_weather", AVAILABLE_TOOLS)
        self.assertTrue(callable(AVAILABLE_TOOLS["get_current_weather"]))

    def test_get_current_weather_schema_shape(self) -> None:
        """get_current_weather definition matches expected OpenAI shape."""
        by_name = {d["function"]["name"]: d for d in TOOL_DEFINITIONS}
        self.assertIn("get_current_weather", by_name)
        fn = by_name["get_current_weather"]["function"]
        self.assertEqual(fn["name"], "get_current_weather")
        self.assertGreater(len(fn["description"]), 0)
        params = fn["parameters"]
        self.assertEqual(params["type"], "object")
        self.assertIn("latitude", params["properties"])
        self.assertIn("longitude", params["properties"])
        self.assertEqual(params["properties"]["latitude"]["type"], "number")
        self.assertEqual(params["properties"]["longitude"]["type"], "number")
        self.assertCountEqual(params["required"], ["latitude", "longitude"])

    def test_get_current_weather_callable(self) -> None:
        """AVAILABLE_TOOLS['get_current_weather'] can be called with latitude, longitude."""
        mock_response = Mock()
        mock_response.json.return_value = {"current": {"temperature_2m": 10}}
        mock_response.raise_for_status = Mock()
        with patch(
            "app.services.ai.tools.get_current_weather.requests.get",
            return_value=mock_response,
        ):
            fn = AVAILABLE_TOOLS["get_current_weather"]
            result = fn(latitude=52.52, longitude=13.405)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, {"current": {"temperature_2m": 10}})
