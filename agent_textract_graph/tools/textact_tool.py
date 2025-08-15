"""Amazon Textract Tool - Extract text from images and PDFs"""

import sys
import os
import boto3
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from strands import Agent, tool
from strands.models import BedrockModel

textract = boto3.client(
    'textract',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config.AWS_SESSION_TOKEN,
    region_name=config.AWS_REGION
)

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

@tool
def textract_tool(file_path: str) -> str:
    """
    Trích xuất văn bản từ hình ảnh sử dụng Amazon Textract
    
    Args:
        file_path: Đường dẫn đến file hình ảnh (jpg, png, pdf)
    
    Returns:
        Văn bản được trích xuất từ hình ảnh
    """
    try:
        if not os.path.exists(file_path):
            return f"❌ Lỗi: File không tồn tại - {file_path}"
        
        with open(file_path, "rb") as document:
            image_bytes = document.read()
        
        response = textract.detect_document_text(Document={'Bytes': image_bytes})
        
        extracted_text = []
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                extracted_text.append(item["Text"])
        
        if extracted_text:
            result = f"""📄 TEXTRACT - Trích xuất văn bản thành công!
            
📁 File: {os.path.basename(file_path)}
📝 Số dòng text: {len(extracted_text)}

📋 NỘI DUNG:
{chr(10).join(extracted_text)}

✅ Hoàn thành!"""
        else:
            result = f"⚠️ Không tìm thấy văn bản trong file: {os.path.basename(file_path)}"
        
        return result
        
    except Exception as e:
        return f"❌ Lỗi khi xử lý file {file_path}: {str(e)}"

def create_textract_agent():
    """
    Tạo Textract Agent với tool đã cấu hình
    
    Returns:
        Agent: Textract agent đã được cấu hình
    """
    textract_agent = Agent(
        model=bedrock_model,
        name="textract",
        tools=[textract_tool],
        system_prompt="""Bạn là chuyên gia trích xuất văn bản từ hình ảnh sử dụng Amazon Textract. 
        
Khi người dùng cung cấp đường dẫn file hình ảnh, hãy sử dụng textract_tool để trích xuất văn bản và trả lời ngắn gọn về kết quả."""
    )
    return textract_agent

