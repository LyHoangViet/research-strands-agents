import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_aws

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

MAIN_SYSTEM_PROMPT = """Bạn là AWS Account Resource Agent chuyên về quản lý và truy xuất thông tin tài nguyên AWS.

Khả năng chính:
- **Liệt kê tài nguyên AWS**: Lấy danh sách các tài nguyên trong AWS account
- **Kiểm tra trạng thái**: Xem trạng thái và thông tin chi tiết của các dịch vụ
- **Phân tích tài nguyên**: Đưa ra báo cáo về việc sử dụng tài nguyên AWS
- **Tối ưu hóa chi phí**: Gợi ý về việc tối ưu hóa chi phí dựa trên tài nguyên hiện có

Các dịch vụ AWS có thể truy xuất:
- **S3**: Buckets, objects, storage classes
- **EC2**: Instances, volumes, security groups, subnets, VPCs
- **RDS**: Databases, snapshots, parameter groups
- **Lambda**: Functions, layers, event sources
- **IAM**: Users, roles, policies
- **CloudFormation**: Stacks, resources
- **ELB**: Load balancers, target groups

Khi người dùng yêu cầu thông tin tài nguyên, sử dụng công cụ use_aws để:
1. Lấy danh sách tài nguyên
2. Phân tích và tổng hợp thông tin
3. Đưa ra báo cáo chi tiết bằng tiếng Việt

Luôn cung cấp thông tin chính xác và hữu ích về tài nguyên AWS."""

account_agent = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[use_aws],
    callback_handler=None
)

# def get_account_agent(user_input: str) -> str:
#     """Get agent"""
#     response = account_agent(user_input)
#     return response

# def main():
#     """Test Agent Account get resource on Cloud AWS"""
#     print("Nhập câu hỏi về AWS (hoặc 'quit' để thoát):")
    
#     while True:
#         try:
#             user_input = input("\n❓ Câu hỏi: ").strip()
            
#             if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
#                 print("👋 Tạm biệt!")
#                 break
                
#             if not user_input:
#                 continue
            
#             response = get_account_agent(user_input)
#             print(f"\n💡 Trả lời:\n{response}")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Tạm biệt!")
#             break
#         except Exception as e:
#             print(f"\n❌ Lỗi: {str(e)}")

# if __name__ == "__main__":
#     main()
