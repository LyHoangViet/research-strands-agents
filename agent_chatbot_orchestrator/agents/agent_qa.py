"""Agent with AWS Documentation Search Tool"""

import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
import config
from agent_chatbot_orchestrator.tools.mcp_docs_aws import get_aws_docs_tools, stdio_mcp_client

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

MAIN_SYSTEM_PROMPT = """Bạn là trợ lý AWS chuyên biệt có thể trả lời các câu hỏi về dịch vụ và tài liệu AWS.

Khi người dùng hỏi về:
- Dịch vụ AWS, tính năng, cấu hình
- Hướng dẫn sử dụng AWS
- Best practices cho AWS
- Troubleshooting AWS

Hãy sử dụng các công cụ tìm kiếm tài liệu AWS để tìm kiếm thông tin chính xác từ tài liệu chính thức của AWS.

Trả lời bằng tiếng Việt và cung cấp thông tin chi tiết, chính xác."""

print("🔧 Initializing AWS tools...")
aws_tools = get_aws_docs_tools()
print(f"✅ Got {len(aws_tools)} AWS tools")

aws_docs_agent = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=aws_tools,
    callback_handler=None
)

# def get_docs_agent(user_input: str) -> str:
#     """Get agent"""
#     response = aws_docs_agent(user_input)
#     return response

# def main():
#     """Test function for AWS documentation agent"""
#     print("🚀 AWS Documentation Agent đã sẵn sàng!")
#     print("Nhập câu hỏi về AWS (hoặc 'quit' để thoát):")
    
#     while True:
#         try:
#             user_input = input("\n❓ Câu hỏi: ").strip()
            
#             if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
#                 print("👋 Tạm biệt!")
#                 break
                
#             if not user_input:
#                 continue
                
#             print("\n🔍 Đang tìm kiếm thông tin...")
#             with stdio_mcp_client:
#                 response = aws_docs_agent(user_input)
#             print(f"\n💡 Trả lời:\n{response}")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Tạm biệt!")
#             break
#         except Exception as e:
#             print(f"\n❌ Lỗi: {str(e)}")

# if __name__ == "__main__":
#     main()

