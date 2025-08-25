import platform
import os
import sys
import atexit
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

# Detect platform
is_windows = sys.platform.startswith('win')
print(f"Detected platform: {'Windows' if is_windows else 'Non-Windows (Linux/macOS)'}")

# Initialize MCP client configuration but don't start it yet
if is_windows:
    print("Using Windows-specific MCP configuration...")
    aws_pricing_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["--from", "awslabs.billing-cost-management-mcp-server@latest", "awslabs.billing-cost-management-mcp-server.exe"],
            env={
                "FASTMCP_LOG_LEVEL": "ERROR",
                "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1")
            }
        )
    ))
else:
    print("Using standard MCP configuration for Linux/macOS...")
    aws_pricing_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["awslabs.billing-cost-management-mcp-server@latest"],
            env={
                "FASTMCP_LOG_LEVEL": "ERROR",
                "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                "AWS_REGION": os.getenv("AWS_REGION", "us-east-1")
            }
        )
    ))

# Global variable to track if client is started
_client_started = False

def get_pricing_tools():
    """Get AWS pricing and billing tools from MCP server"""
    global _client_started
    
    try:
        # Start MCP client only if not already started
        if not _client_started:
            print("Starting AWS Pricing MCP client...")
            aws_pricing_mcp_client.start()
            print("AWS Pricing MCP client started successfully.")
            _client_started = True
        
        tools = aws_pricing_mcp_client.list_tools_sync()
        print(f"💰 Pricing MCP Tools found: {len(tools) if tools else 0}")
        
        if tools:
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool.tool_name}")
        
        return tools
    except Exception as e:
        error_message = str(e)
        print(f"❌ Error getting pricing tools: {error_message}")
        
        if is_windows:
            print("\nWindows-specific troubleshooting tips:")
            print("1. Ensure you have installed the 'uv' package: pip install uv")
            print("2. Check if you have proper permissions to execute the commands")
            print("3. Verify your network connection and firewall settings")
            print("4. Ensure your AWS credentials are properly configured")
            print("5. Try running: uvx --help to test uvx installation")
        else:
            print("\nTroubleshooting tips:")
            print("1. Ensure you have installed uvx: pip install uv")
            print("2. Check your network connection")
            print("3. Verify your AWS credentials are configured")
        
        return []

stdio_mcp_client = aws_pricing_mcp_client

def cleanup():
    try:
        if hasattr(aws_pricing_mcp_client, '__exit__'):
            aws_pricing_mcp_client.__exit__(None, None, None)
        print("AWS Pricing MCP client stopped")
    except Exception as e:
        print(f"Error stopping AWS Pricing MCP client: {e}")

atexit.register(cleanup)