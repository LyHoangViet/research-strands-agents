"""Test Agent Orchestrator with Agents as Tools pattern"""

import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from agent_chatbot_orchestrator.agents.agent_account import get_account_agent
from agent_chatbot_orchestrator.agents.agent_architect import get_architect_agent
from agent_chatbot_orchestrator.agents.agent_qa import get_docs_agent


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

MAIN_SYSTEM_PROMPT = """
Bạn là trợ lý thông minh, có nhiệm vụ điều phối truy vấn của người dùng đến các agent chuyên biệt.
Luôn lựa chọn agent phù hợp nhất dựa trên nội dung câu hỏi, và khi đã chọn được agent, hãy gọi tool tương ứng 
với toàn bộ câu hỏi của người dùng (user_input) làm input cho tool đó. 
Sau đó, sử dụng output từ tool để trả lời người dùng.

Các lựa chọn:
- Nếu người dùng muốn **xem hoặc lấy thông tin về các resource đang sử dụng trong AWS account** → gọi tool **get_account_agent(user_input)**
- Nếu người dùng muốn **thiết kế, vẽ hoặc tư vấn về kiến trúc hệ thống trên AWS** → gọi tool **get_architect_agent(user_input)**
- Nếu người dùng muốn **tìm kiếm, tham khảo hoặc đọc hướng dẫn chính thức từ tài liệu AWS** → gọi tool **get_docs_agent(user_input)**
- Nếu câu hỏi đơn giản, không thuộc phạm vi các agent trên → trả lời trực tiếp.

Luôn ưu tiên chọn tool phù hợp nhất. 
Nếu chưa rõ người dùng cần gì, hãy hỏi lại để làm rõ.
Trả lời bằng tiếng Việt.
"""

orchestrator = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[get_account_agent, get_architect_agent, get_docs_agent],
    callback_handler=None
)

def main():
    """Test Agent Account get resource on Cloud AWS"""
    print("Nhập câu hỏi về AWS (hoặc 'quit' để thoát):")
    
    while True:
        try:
            user_input = input("\n❓ Câu hỏi: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
                print("👋 Tạm biệt!")
                break
                
            if not user_input:
                continue
            
            response = orchestrator(user_input)
            print(f"\n💡 Trả lời:\n{response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
