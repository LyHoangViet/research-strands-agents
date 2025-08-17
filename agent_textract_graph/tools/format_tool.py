"""Format Tool - Format output to structured JSON using LLM"""

import sys
import os
import boto3
import logging
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from strands import Agent
from strands.models import BedrockModel

boto_session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config.AWS_SESSION_TOKEN,
    region_name=config.AWS_REGION
)

bedrock_model = BedrockModel(
    boto_session=boto_session,
    model_id=config.CHATBOT_AGENT_MODEL,
    temperature=0.1,  
    max_tokens=5000,
)

def create_format_agent():
    """
    Tạo Format Agent để format kết quả thành JSON bằng LLM
    
    Returns:
        Agent: Format agent đã được cấu hình
    """
    format_agent = Agent(
        model=bedrock_model,
        name="document_formatter",
        system_prompt="""Bạn là chuyên gia format dữ liệu tài liệu thành JSON.

Nhiệm vụ của bạn:
- Nhận kết quả từ các bước xử lý trước (Textract, Classification, Extraction)
- Format thành JSON output cuối cùng theo đúng format yêu cầu
- Đảm bảo JSON có thể parse được và đúng cấu trúc

FORMAT JSON YÊU CẦU:
{
  "loai_giay_to": "Identity/Address/Eligibility",
  "ten_giay_to": "Tên cụ thể của giấy tờ",
  "cac_truong_du_lieu": {
    "field_name": "field_value",
    "ho_va_ten": "Nguyễn Văn A",
    "ngay_sinh": "01/01/1990"
  },
  "canh_bao_chat_luong_anh": ["warning1", "warning2"] hoặc null
}

QUY TẮC:
- Trích xuất chính xác thông tin từ kết quả classification và extraction
- Chuyển đổi tên trường sang snake_case (VD: "Họ và tên" → "ho_va_ten")
- Chuẩn hóa ngày tháng về format DD/MM/YYYY
- Tạo cảnh báo nếu có vấn đề về chất lượng
- Chỉ trả về JSON, không thêm text giải thích

Luôn trả về JSON hợp lệ, chính xác và đầy đủ."""
    )
    return format_agent