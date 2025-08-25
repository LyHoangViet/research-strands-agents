"""Agent with AWS Pricing and Billing Tools"""

import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
import config
from agent_chatbot_orchestrator.tools.mcp_pricing import get_pricing_tools, stdio_mcp_client

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

MAIN_SYSTEM_PROMPT = """Bạn là trợ lý AWS chuyên biệt về chi phí và thanh toán có thể trả lời các câu hỏi về:

- Chi phí dịch vụ AWS và tính toán giá cả
- Quản lý billing và cost management
- Tối ưu hóa chi phí AWS
- Phân tích usage và spending
- Reserved Instances và Savings Plans
- Cost allocation và budgeting

Hãy sử dụng các công cụ pricing và billing để tìm kiếm thông tin chính xác về chi phí AWS.

Trả lời bằng tiếng Việt và cung cấp thông tin chi tiết, chính xác về chi phí."""

print("💰 Initializing AWS Pricing tools...")
pricing_tools = get_pricing_tools()
print(f"✅ Got {len(pricing_tools)} AWS pricing tools")

aws_pricing_agent = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=pricing_tools,
    callback_handler=None
)

def get_pricing_agent(user_input: str) -> str:
    """Get pricing agent response"""
    response = aws_pricing_agent(user_input)
    return response

def test_pricing_tools():
    """Test function to check MCP pricing tools"""
    print("🧪 Testing AWS Pricing MCP Tools...")
    
    try:
        # Test getting tools
        tools = get_pricing_tools()
        print(f"✅ Successfully loaded {len(tools)} pricing tools")
        
        # Test a simple query first without MCP tools
        simple_query = "Hello, can you help me with AWS pricing?"
        print(f"\n🔍 Testing simple query: {simple_query}")
        
        # Create a simple agent without MCP tools for testing
        simple_agent = Agent(
            model=bedrock_model,
            system_prompt="You are a helpful AWS pricing assistant. Answer briefly.",
            tools=[],  # No tools for simple test
            callback_handler=None
        )
        
        response = simple_agent(simple_query)
        print(f"\n💡 Simple Response:\n{response}")
        
        # Now test with MCP tools if simple test works
        print(f"\n🔍 Testing MCP query...")
        mcp_query = "What is AWS pricing?"
        response = aws_pricing_agent(mcp_query)
        print(f"\n💡 MCP Response:\n{response}")
        
    except Exception as e:
        print(f"❌ Error testing pricing tools: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Test function for AWS pricing agent"""
    print("🚀 AWS Pricing Agent đã sẵn sàng!")
    print("Nhập câu hỏi về chi phí AWS (hoặc 'quit' để thoát):")
    print("Gợi ý: Thử câu hỏi đơn giản trước như 'Hello' hoặc 'What is AWS?'")
    
    while True:
        try:
            user_input = input("\n❓ Câu hỏi: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
                print("👋 Tạm biệt!")
                break
                
            if not user_input:
                continue
                
            print("\n🔍 Đang xử lý câu hỏi...")
            
            # Try with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = aws_pricing_agent(user_input)
                    print(f"\n💡 Trả lời:\n{response}")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Thử lại lần {attempt + 2}...")
                        continue
                    else:
                        raise e
            
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {str(e)}")
            print("💡 Thử câu hỏi đơn giản hơn hoặc kiểm tra kết nối mạng.")

if __name__ == "__main__":
    test_pricing_tools()
    
    main()

