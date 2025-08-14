"""Test Strands Agent with direct config variables and A2A functionality"""
import sys
import os
import boto3
import logging
import threading
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from strands import Agent
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer

try:
    from strands_tools.calculator import calculator
    print("✅ Calculator tool imported")
except ImportError:
    print("⚠️ Calculator tool not available")
    calculator = None

logging.basicConfig(level=logging.INFO)

boto_session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config.AWS_SESSION_TOKEN,
    region_name=config.AWS_REGION
)

bedrock_model = BedrockModel(
    boto_session=boto_session,
    model_id=config.CHATBOT_AGENT_MODEL,
    temperature=config.BEDROCK_TEMPERATURE,
    max_tokens=config.BEDROCK_MAX_TOKENS,
)

tools = [calculator] if calculator else []
agent = Agent(
    model=bedrock_model,
    name="Calculator Agent",
    description="A calculator agent that can perform basic arithmetic operations.",
    tools=tools,
    callback_handler=None
)

a2a_server = A2AServer(agent=agent)

def test_basic_agent():
    """Test basic agent functionality"""
    print("=== Test Basic Agent ===")
    
    try:
        # Test simple chat
        response = agent("Hello! How are you?")
        print(f"User: Hello! How are you?")
        print(f"Agent: {str(response)}")
        
        # Test with calculator if available
        if calculator:
            print("\n--- Testing Calculator ---")
            calc_response = agent("What is 15 + 25?")
            print(f"User: What is 15 + 25?")
            print(f"Agent: {str(calc_response)}")
        
        print("✅ Basic agent test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_a2a_server():
    """Test A2A server"""
    print("\n=== Test A2A Server ===")
    
    try:
        print(f"Agent name: {agent.name}")
        print(f"Agent description: {agent.description}")
        print(f"Tools available: {len(tools)} tools")
        
        def start_server():
            try:
                print("🚀 Starting A2A server...")
                a2a_server.serve()
            except Exception as e:
                print(f"Server error: {e}")
        
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        
        time.sleep(2)
        print("✅ A2A Server started in background!")
        print("💡 Server is running... Press Ctrl+C to stop")
        
        # Keep main thread alive for a bit
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run tests"""
    print("Testing Strands Agent with A2A")
    print("=" * 40)
    
    print(f"Model: {config.CHATBOT_AGENT_MODEL}")
    print(f"Region: {config.AWS_REGION}")
    print(f"Temperature: {config.BEDROCK_TEMPERATURE}")
    print(f"Max Tokens: {config.BEDROCK_MAX_TOKENS}")
    
    # Run tests
    test_basic_agent()
    test_a2a_server()
    
    print("\n" + "=" * 40)
    print("Tests completed!")


if __name__ == "__main__":
    main()
