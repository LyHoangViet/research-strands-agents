"""AWS Architect Agent with Diagram Generation"""

import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel
from strands_tools import diagram

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
import config

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

MAIN_SYSTEM_PROMPT = """Bạn là AWS Architect Agent chuyên về vẽ sơ đồ kiến trúc AWS.

Khả năng chính:
- **Vẽ sơ đồ kiến trúc AWS**: Tạo sơ đồ architecture dựa trên mô tả của người dùng
- **Tư vấn kiến trúc**: Đưa ra gợi ý về kiến trúc AWS phù hợp
- **Giải thích các thành phần**: Mô tả các dịch vụ AWS trong kiến trúc

Khi người dùng yêu cầu vẽ sơ đồ, sử dụng công cụ diagram với:
- diagram_type="cloud" cho sơ đồ AWS
- nodes: danh sách các thành phần với id, type (tên dịch vụ AWS), label
- edges: kết nối giữa các thành phần với from, to
- title: tiêu đề sơ đồ (QUAN TRỌNG: Chỉ sử dụng tiếng Anh cho title để tránh lỗi encoding)

Các loại AWS services phổ biến: Users, CloudFront, S3, APIGateway, Lambda, EC2, RDS, DynamoDB, ELB, VPC, etc.

Ví dụ title tiếng Anh: "Web Application Architecture", "Serverless Architecture", "Microservices on EKS"

Luôn trả lời bằng tiếng Việt và cung cấp thông tin chi tiết về kiến trúc AWS."""


def get_diagram_tools():
    """Get diagram tools for AWS architecture"""
    if hasattr(diagram, 'diagram'):
        return [diagram.diagram]
    elif hasattr(diagram, 'tool'):
        return [diagram.tool]
    else:
        tools = []
        for attr_name in dir(diagram):
            attr = getattr(diagram, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                tools.append(attr)
        return tools


print("🔧 Initializing AWS diagram tools...")
diagram_tools = get_diagram_tools()
print(f"✅ Got {len(diagram_tools)} AWS diagram tools")

aws_architect_agent = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=diagram_tools,
    callback_handler=None
)

# def get_architect_agent(user_input: str) -> str:
#     """Invoke AWS Architect Agent"""
#     response = aws_architect_agent(user_input)
#     return response

# def main():
#     """Test function for AWS architect agent"""
#     print("🚀 AWS Architect Agent đã sẵn sàng!")
#     print("Chuyên về vẽ sơ đồ kiến trúc AWS")
#     print("Ví dụ:")
#     print("  - 'Vẽ sơ đồ web app với ALB, EC2, RDS'")
#     print("  - 'Tạo sơ đồ serverless với Lambda và DynamoDB'")
#     print("  - 'Vẽ kiến trúc microservices trên EKS'")
#     print("  - 'Liệt kê các icons có sẵn'")
#     print("\nNhập yêu cầu (hoặc 'quit' để thoát):")
    
#     while True:
#         try:
#             user_input = input("\n🎨 Yêu cầu: ").strip()
            
#             if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
#                 print("👋 Tạm biệt!")
#                 break
                
#             if not user_input:
#                 continue
                
#             print("\n🔍 Đang tạo sơ đồ...")
            
#             response = aws_architect_agent(user_input)
#             print(f"\n💡 Kết quả:\n{response}")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Tạm biệt!")
#             break
#         except Exception as e:
#             print(f"\n❌ Lỗi: {str(e)}")

# if __name__ == "__main__":
#     main()

