from plugins.tools.web_search import WebSearchPlugin
from plugins.tools.file_tool import FileManagerPlugin
from plugins.tools.weather import WeatherPlugin
from plugins.plugin_manager import PluginManager

class ToolExecutor:
    """Gives AI agents the ability to use real tools"""

    @staticmethod
    def get_available_tools() -> list:
        """Get list of enabled tools"""
        enabled = PluginManager.get_enabled_plugins()
        tools = []

        if "web_search" in enabled:
            tools.append({
                "name": "web_search",
                "description": "Search the internet for real-time information",
                "usage": "web_search(query)"
            })

        if "file_manager" in enabled:
            tools.append({
                "name": "save_file",
                "description": "Save content to a file",
                "usage": "save_file(filename, content)"
            })

        if "weather" in enabled:
            tools.append({
                "name": "get_weather",
                "description": "Get weather for a city",
                "usage": "get_weather(city)"
            })

        return tools

    @staticmethod
    def execute_tool(tool_name: str, **kwargs) -> str:
        """Execute a specific tool and return result as string"""

        print(f"🔧 Executing tool: {tool_name} with {kwargs}")

        if tool_name == "web_search":
            query = kwargs.get("query", "")
            result = WebSearchPlugin.search(query, max_results=3)

            if result["success"] and result["results"]:
                output = f"Web Search Results for '{query}':\n\n"
                for i, r in enumerate(result["results"], 1):
                    output += f"{i}. {r['title']}\n"
                    output += f"   {r['snippet'][:200]}\n"
                    if r.get('url'):
                        output += f"   URL: {r['url']}\n"
                    output += "\n"
                return output
            return f"No results found for: {query}"

        elif tool_name == "save_file":
            filename = kwargs.get("filename", "nexus_output.txt")
            content = kwargs.get("content", "")
            result = FileManagerPlugin.write_file(filename, content)
            if result["success"]:
                return f"File '{filename}' saved successfully ({result['size']} bytes)"
            return f"Failed to save file: {result.get('error', 'Unknown error')}"

        elif tool_name == "get_weather":
            city = kwargs.get("city", "Karachi")
            result = WeatherPlugin.get_weather(city)
            if result["success"]:
                return (
                    f"Weather in {result['city']}, {result['country']}:\n"
                    f"Temperature: {result['temperature']}°C (Feels like {result['feels_like']}°C)\n"
                    f"Condition: {result['description']}\n"
                    f"Humidity: {result['humidity']}%\n"
                    f"Wind: {result['wind_speed']} m/s"
                )
            return f"Weather error: {result.get('error', 'Unknown')}"

        return f"Unknown tool: {tool_name}"

    @staticmethod
    def parse_and_execute(ai_response: str) -> tuple:
        """Parse AI response for tool calls and execute them"""
        import re

        tool_results = []
        modified_response = ai_response

        # Pattern: [TOOL: tool_name(param="value")]
        pattern = r'\[TOOL:\s*(\w+)\(([^)]*)\)\]'
        matches = re.finditer(pattern, ai_response)

        for match in matches:
            tool_name = match.group(1)
            params_str = match.group(2)

            # Parse params
            params = {}
            param_pattern = r'(\w+)="([^"]*)"'
            for param_match in re.finditer(param_pattern, params_str):
                params[param_match.group(1)] = param_match.group(2)

            # Execute tool
            result = ToolExecutor.execute_tool(tool_name, **params)
            tool_results.append({
                "tool": tool_name,
                "params": params,
                "result": result
            })

            # Replace tool call with result
            modified_response = modified_response.replace(
                match.group(0),
                f"\n[Tool Result - {tool_name}]\n{result}\n"
            )

        return modified_response, tool_results