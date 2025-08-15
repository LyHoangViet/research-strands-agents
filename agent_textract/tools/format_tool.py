"""Format Tool - Format output to structured JSON"""

import sys
import os
import boto3
import logging
import json
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from strands import Agent, tool
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

@tool
def create_final_json_output(textract_result: str, classification_result: str, extraction_result: str, multiple_docs_result: str = None, multiple_entities_result: str = None) -> str:
    """
    Tạo JSON output cuối cùng theo đúng format yêu cầu
    
    Args:
        textract_result: Kết quả Textract
        classification_result: Kết quả phân loại
        extraction_result: Kết quả trích xuất
        multiple_docs_result: Kết quả phát hiện nhiều tài liệu (optional)
        multiple_entities_result: Kết quả phát hiện nhiều thực thể (optional)
    
    Returns:
        JSON output cuối cùng theo format yêu cầu
    """
    
    # Parse classification
    category = "Unknown"
    document_type = "Unknown"
    confidence_score = 0
    
    if classification_result:
        if "Category:" in classification_result:
            category_match = re.search(r'Category:\s*([^\n]+)', classification_result)
            if category_match:
                category = category_match.group(1).strip()
        
        if "Document Type:" in classification_result:
            doc_type_match = re.search(r'Document Type:\s*([^\n]+)', classification_result)
            if doc_type_match:
                document_type = doc_type_match.group(1).strip()
        
        if "Confidence Score:" in classification_result:
            confidence_match = re.search(r'Confidence Score:\s*(\d+)', classification_result)
            if confidence_match:
                confidence_score = int(confidence_match.group(1))
    
    # Parse extracted fields
    extracted_fields = {}
    if extraction_result and "📝" in extraction_result:
        field_lines = extraction_result.split('\n')
        for line in field_lines:
            if "📝" in line and ":" in line:
                field_match = re.search(r'📝\s*([^:]+):\s*(.+)', line)
                if field_match:
                    field_name = field_match.group(1).strip().lower().replace(' ', '_')
                    field_value = field_match.group(2).strip()
                    extracted_fields[field_name] = field_value
    
    # Generate quality warnings
    warnings = []
    
    # Check for multiple documents
    if multiple_docs_result and "MULTIPLE DOCUMENTS DETECTED" in multiple_docs_result:
        warnings.append("Multiple documents detected in single image")
    
    # Check for multiple entities
    if multiple_entities_result and "MULTIPLE ENTITIES DETECTED" in multiple_entities_result:
        warnings.append("Multiple entities detected in document")
    
    # Check confidence
    if confidence_score < 5:
        warnings.append("Low classification confidence - manual review recommended")
    
    # Check textract quality
    if textract_result and "Confidence:" in textract_result:
        confidence_match = re.search(r'Confidence:\s*([\d.]+)', textract_result)
        if confidence_match:
            ocr_confidence = float(confidence_match.group(1))
            if ocr_confidence < 80:
                warnings.append("Low OCR confidence - image may be blurry or low quality")
    
    # Final JSON according to requirements
    final_output = {
        "loai_giay_to": category,
        "ten_giay_to": document_type,
        "cac_truong_du_lieu": extracted_fields,
        "canh_bao_chat_luong_anh": warnings if warnings else None
    }
    
    return json.dumps(final_output, ensure_ascii=False, indent=2)

def create_format_agent():
    """
    Tạo Format Agent với tool create_final_json_output
    
    Returns:
        Agent: Format agent đã được cấu hình
    """
    format_agent = Agent(
        model=bedrock_model,
        name="document_formatter",
        tools=[create_final_json_output],
        system_prompt="""Bạn là chuyên gia format dữ liệu tài liệu thành JSON.

Nhiệm vụ của bạn:
- Tạo JSON output cuối cùng theo format yêu cầu:
  * loai_giay_to: Category của tài liệu (Identity/Address/Eligibility)
  * ten_giay_to: Tên cụ thể của giấy tờ (Driver's License, Passport, v.v.)
  * cac_truong_du_lieu: Các trường đã trích xuất (name, date_of_birth, v.v.)
  * canh_bao_chat_luong_anh: Cảnh báo nếu có (array hoặc null)

Luôn sử dụng create_final_json_output để tạo kết quả cuối cùng.
Đảm bảo JSON output đúng format và có thể parse được.
Trả lời bằng tiếng Việt, chính xác và đầy đủ."""
    )
    return format_agent