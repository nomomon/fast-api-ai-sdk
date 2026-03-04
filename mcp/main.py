from fastmcp import FastMCP

from tools.files import edit_file, list_dir, read_file, write_file
from tools.shell import run_bash, run_python

mcp = FastMCP("Demo 🚀")

for fn in [read_file, list_dir, edit_file, write_file, run_python, run_bash]:
    mcp.tool(fn)


if __name__ == "__main__":
    # Bind to 0.0.0.0 so other containers (e.g. backend) can reach this server
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
    )
