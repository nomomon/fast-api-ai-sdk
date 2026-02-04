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


def _tool_with_default(a: int, b: int = 1) -> str:
    """Tool with a default parameter."""
    return f"{a},{b}"


def _tool_with_optional(x: str | None) -> str:
    """Tool with optional parameter (pipe syntax)."""
    return x or ""


def _tool_complex_types(
    ids: list[int],
    counts: dict[str, int],
    value: str | int,
) -> str:
    """Tool with list, dict, and union type args."""
    return str(ids) + str(counts) + str(value)


def _tool_no_docstring(a: int, b: str) -> bool:
    return True


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

    def test_default_parameter_not_required(self) -> None:
        """Parameters with default values are not in required."""
        result = function_to_openai_tool("_tool_with_default", _tool_with_default)
        required = result["function"]["parameters"]["required"]
        self.assertIn("a", required)
        self.assertNotIn("b", required)
        props = result["function"]["parameters"]["properties"]
        self.assertEqual(props["b"]["type"], "integer")

    def test_optional_parameter_not_required(self) -> None:
        """Optional (str | None) parameter is not in required."""
        result = function_to_openai_tool("_tool_with_optional", _tool_with_optional)
        required = result["function"]["parameters"]["required"]
        self.assertNotIn("x", required)
        props = result["function"]["parameters"]["properties"]
        self.assertEqual(props["x"]["type"], "string")

    def test_complex_type_annotations(self) -> None:
        """list[int], dict[str, int], and str | int get correct schema."""
        result = function_to_openai_tool("_tool_complex_types", _tool_complex_types)
        props = result["function"]["parameters"]["properties"]
        self.assertEqual(props["ids"]["type"], "array")
        self.assertIn("items", props["ids"])
        self.assertEqual(props["ids"]["items"]["type"], "integer")
        self.assertEqual(props["counts"]["type"], "object")
        self.assertIn("additionalProperties", props["counts"])
        self.assertEqual(props["counts"]["additionalProperties"]["type"], "integer")
        self.assertEqual(props["value"]["type"], "string")

    def test_function_without_docstring(self) -> None:
        """Function without docstring gets empty description and types from annotations."""
        result = function_to_openai_tool("_tool_no_docstring", _tool_no_docstring)
        fn = result["function"]
        self.assertEqual(fn["description"], "")
        props = fn["parameters"]["properties"]
        self.assertEqual(props["a"]["type"], "integer")
        self.assertEqual(props["b"]["type"], "string")


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
