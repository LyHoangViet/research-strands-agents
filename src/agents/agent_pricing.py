"""Test Agent Orchestrator with Agents as Tools pattern"""

import sys
import os
import boto3
import logging
from strands import Agent
from strands.models import BedrockModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

MAIN_SYSTEM_PROMPT = """Bạn là trợ lý thông minh điều phối các truy vấn đến các agent chuyên biệt:

- Đối với câu hỏi nghiên cứu và thông tin thực tế → Sử dụng công cụ research_assistant
- Đối với tư vấn sản phẩm và mua sắm → Sử dụng công cụ product_recommendation_assistant  
- Đối với lập kế hoạch du lịch và lịch trình → Sử dụng công cụ trip_planning_assistant
- Đối với câu hỏi đơn giản không cần kiến thức chuyên môn → Trả lời trực tiếp

Luôn chọn công cụ phù hợp nhất dựa trên truy vấn của người dùng. Nếu không chắc chắn, hãy yêu cầu làm rõ.
Trả lời bằng tiếng Việt."""

orchestrator = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[research_assistant, product_recommendation_assistant, trip_planning_assistant],
    callback_handler=None
)

