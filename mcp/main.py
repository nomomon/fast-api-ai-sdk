from fastmcp import FastMCP
from tools.files import mcp as files_mcp
from tools.shell import mcp as shell_mcp

mcp = FastMCP("Demo 🚀")
mcp.mount(files_mcp, prefix="files")
mcp.mount(shell_mcp, prefix="shell")


if __name__ == "__main__":
    # Bind to 0.0.0.0 so other containers (e.g. backend) can reach this server
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
    )
