import platform
import os
import sys
import atexit
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

# Detect platform
is_windows = sys.platform.startswith('win')
print(f"Detected platform: {'Windows' if is_windows else 'Non-Windows (Linux/macOS)'}")

# Create MCP client based on platform
try:
    if is_windows:
        # Windows-specific configuration
        print("Using Windows-specific MCP configuration...")
        aws_diagram_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uv",
                args=["tool", "run", "--from", "awslabs.aws-diagram-mcp-server@latest", "awslabs.aws-diagram-mcp-server.exe"],
                env={
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                    "AWS_REGION": os.getenv("AWS_REGION", "us-east-1")
                }
            )
        ))
    else:
        # Non-Windows configuration (Linux/macOS)
        print("Using standard MCP configuration for Linux/macOS...")
        aws_diagram_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx", 
                args=["awslabs.aws-diagram-mcp-server@latest"],
                env={
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                    "AWS_REGION": os.getenv("AWS_REGION", "us-east-1")
                }
            )
        ))

    # Start MCP client
    print("Starting AWS Diagram MCP client...")
    aws_diagram_mcp_client.start()
    print("AWS Diagram MCP client started successfully.")
    
except Exception as e:
    error_message = str(e)
    print(f"Error initializing MCP client: {error_message}")
    
    if is_windows:
        print("\nWindows-specific troubleshooting tips:")
        print("1. Ensure you have installed the 'uv' package: pip install uv")
        print("2. Check if you have proper permissions to execute the commands")
        print("3. Verify your network connection and firewall settings")
    else:
        print("\nTroubleshooting tips:")
        print("1. Ensure you have installed uvx: pip install uv")
        print("2. Check your network connection")
    
    # Re-raise the exception
    raise

def get_diagram_tools():
    """Get AWS diagram tools from MCP server"""
    try:
        tools = aws_diagram_mcp_client.list_tools_sync()
        print(f"🎨 Diagram MCP Tools found: {len(tools) if tools else 0}")
        
        if tools:
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool.tool_name}")
        
        return tools
    except Exception as e:
        print(f"❌ Error getting diagram tools: {e}")
        return []

# Export the client for use in other modules
stdio_mcp_client = aws_diagram_mcp_client

# Register cleanup handler
def cleanup():
    try:
        if hasattr(aws_diagram_mcp_client, '__exit__'):
            aws_diagram_mcp_client.__exit__(None, None, None)
        print("AWS Diagram MCP client stopped")
    except Exception as e:
        print(f"Error stopping AWS Diagram MCP client: {e}")

atexit.register(cleanup)
