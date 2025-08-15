import platform
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

stdio_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="uvx", 
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
))

if platform.system() == "Windows":
    stdio_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=[
                "--from", 
                "awslabs.aws-documentation-mcp-server@latest", 
                "awslabs.aws-documentation-mcp-server.exe"
            ]
        )
    ))

def get_aws_docs_tools():
    """Get AWS documentation tools from MCP server"""
    try:
        with stdio_mcp_client:
            tools = stdio_mcp_client.list_tools_sync()
            return tools
    except Exception as e:
        print(f"Error getting AWS docs tools: {e}")
        return []
