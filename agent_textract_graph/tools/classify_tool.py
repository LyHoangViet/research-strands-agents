"""Document Classification Tool - Classify and extract data from documents"""

import sys
import os
import boto3
import logging
import json
import re
from typing import Dict, List, Any

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
def classify_document_type(extracted_text: str) -> str:
    """
    Phân loại loại giấy tờ dựa trên văn bản đã trích xuất
    
    Args:
        extracted_text: Văn bản đã được trích xuất từ Textract
    
    Returns:
        Kết quả phân loại với category và document type
    """
    
    identity_keywords = [
        'driver', 'license', 'passport', 'id card', 'identity', 'citizen', 'national id',
        'bằng lái xe', 'hộ chiếu', 'chứng minh', 'căn cước', 'giấy tờ tùy thân'
    ]
    
    address_keywords = [
        'utility bill', 'bank statement', 'lease', 'rental', 'address', 'residence',
        'hóa đơn điện', 'hóa đơn nước', 'sao kê ngân hàng', 'hợp đồng thuê', 'địa chỉ'
    ]
    
    eligibility_keywords = [
        'certificate', 'diploma', 'degree', 'qualification', 'employment', 'income',
        'bằng cấp', 'chứng chỉ', 'văn bằng', 'giấy chứng nhận', 'thu nhập'
    ]
    
    text_lower = extracted_text.lower()
    
    identity_score = sum(1 for keyword in identity_keywords if keyword in text_lower)
    address_score = sum(1 for keyword in address_keywords if keyword in text_lower)
    eligibility_score = sum(1 for keyword in eligibility_keywords if keyword in text_lower)
    
    scores = {
        'Identity': identity_score,
        'Address': address_score, 
        'Eligibility': eligibility_score
    }
    
    category = max(scores, key=scores.get)
    confidence = max(scores.values())
    
    document_type = "Unknown"
    
    if category == "Identity":
        if any(word in text_lower for word in ['driver', 'license', 'bằng lái']):
            document_type = "Driver's License"
        elif any(word in text_lower for word in ['passport', 'hộ chiếu']):
            document_type = "Passport"
        elif any(word in text_lower for word in ['id card', 'identity', 'căn cước', 'chứng minh']):
            document_type = "ID Card"
    
    elif category == "Address":
        if any(word in text_lower for word in ['utility', 'electric', 'water', 'điện', 'nước']):
            document_type = "Utility Bill"
        elif any(word in text_lower for word in ['bank', 'statement', 'ngân hàng', 'sao kê']):
            document_type = "Bank Statement"
        elif any(word in text_lower for word in ['lease', 'rental', 'thuê']):
            document_type = "Lease Agreement"
    
    elif category == "Eligibility":
        if any(word in text_lower for word in ['certificate', 'chứng chỉ']):
            document_type = "Certificate"
        elif any(word in text_lower for word in ['diploma', 'degree', 'bằng']):
            document_type = "Diploma/Degree"
        elif any(word in text_lower for word in ['employment', 'income', 'thu nhập']):
            document_type = "Employment Document"
    
    result = f"""📋 DOCUMENT CLASSIFICATION
    
🏷️ Category: {category}
📄 Document Type: {document_type}
🎯 Confidence Score: {confidence}/10
📊 Scores: Identity({identity_score}) | Address({address_score}) | Eligibility({eligibility_score})

✅ Classification completed!"""
    
    return result

@tool
def extract_key_fields(extracted_text: str, document_category: str) -> str:
    """
    Trích xuất các trường dữ liệu quan trọng dựa trên loại tài liệu
    
    Args:
        extracted_text: Văn bản đã được trích xuất
        document_category: Loại tài liệu (Identity/Address/Eligibility)
    
    Returns:
        Các trường dữ liệu đã được trích xuất
    """
    
    extracted_fields = {}
    text_lines = extracted_text.split('\n')
    
    patterns = {
        'name': r'(?:name|tên|họ tên)[:\s]*([A-Za-z\s]+)',
        'date_of_birth': r'(?:dob|date of birth|ngày sinh|sinh)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        'id_number': r'(?:id|number|số)[:\s]*([A-Z0-9]+)',
        'address': r'(?:address|địa chỉ)[:\s]*([^,\n]+)',
        'phone': r'(?:phone|tel|điện thoại)[:\s]*(\d{10,11})',
        'email': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    }
    
    if document_category.lower() == "identity":
        for field, pattern in patterns.items():
            if field in ['name', 'date_of_birth', 'id_number', 'address']:
                matches = re.findall(pattern, extracted_text, re.IGNORECASE)
                if matches:
                    extracted_fields[field] = matches[0].strip()
    
    elif document_category.lower() == "address":
        for field, pattern in patterns.items():
            if field in ['name', 'address', 'phone']:
                matches = re.findall(pattern, extracted_text, re.IGNORECASE)
                if matches:
                    extracted_fields[field] = matches[0].strip()
    
    elif document_category.lower() == "eligibility":
        for field, pattern in patterns.items():
            if field in ['name', 'date_of_birth', 'id_number']:
                matches = re.findall(pattern, extracted_text, re.IGNORECASE)
                if matches:
                    extracted_fields[field] = matches[0].strip()
    
    # Format kết quả
    if extracted_fields:
        result = f"""🔍 EXTRACTED KEY FIELDS ({document_category.upper()})
        
"""
        for field, value in extracted_fields.items():
            result += f"📝 {field.replace('_', ' ').title()}: {value}\n"
        
        result += "\n✅ Field extraction completed!"
    else:
        result = f"⚠️ Không tìm thấy trường dữ liệu nào cho category: {document_category}"
    
    return result

@tool
def detect_multiple_documents(extracted_text: str) -> str:
    """
    Phát hiện và xử lý trường hợp một ảnh có nhiều loại giấy tờ
    
    Args:
        extracted_text: Văn bản đã được trích xuất
    
    Returns:
        Thông tin về các tài liệu được phát hiện
    """
    
    document_indicators = {
        "Driver's License": ['driver', 'license', 'class', 'endorsements', 'bằng lái'],
        "Passport": ['passport', 'nationality', 'place of birth', 'hộ chiếu'],
        "ID Card": ['identity card', 'citizen', 'id number', 'căn cước', 'chứng minh'],
        "Utility Bill": ['utility', 'electric', 'water', 'gas', 'hóa đơn'],
        "Bank Statement": ['bank', 'statement', 'balance', 'account', 'ngân hàng'],
        "Certificate": ['certificate', 'certify', 'awarded', 'chứng chỉ', 'chứng nhận']
    }
    
    detected_documents = []
    text_lower = extracted_text.lower()
    
    for doc_type, keywords in document_indicators.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score >= 2:  # Threshold để xác định có tài liệu
            detected_documents.append({
                'type': doc_type,
                'confidence': score
            })
    
    detected_documents.sort(key=lambda x: x['confidence'], reverse=True)
    
    if len(detected_documents) > 1:
        result = f"""🔍 MULTIPLE DOCUMENTS DETECTED
        
📊 Found {len(detected_documents)} document types:

"""
        for i, doc in enumerate(detected_documents, 1):
            result += f"{i}. {doc['type']} (confidence: {doc['confidence']})\n"
        
        result += f"""
⚠️ RECOMMENDATION:
- Xử lý từng tài liệu riêng biệt
- Ưu tiên tài liệu có confidence cao nhất
- Kiểm tra lại kết quả trích xuất

✅ Multi-document detection completed!"""
    
    elif len(detected_documents) == 1:
        result = f"""📄 SINGLE DOCUMENT DETECTED
        
🏷️ Document Type: {detected_documents[0]['type']}
🎯 Confidence: {detected_documents[0]['confidence']}

✅ Single document confirmed!"""
    
    else:
        result = "⚠️ Không thể xác định loại tài liệu rõ ràng. Cần kiểm tra lại."
    
    return result

@tool
def handle_multiple_entities(extracted_text: str) -> str:
    """
    Xử lý trường hợp một tài liệu có nhiều thực thể (người, địa chỉ, v.v.)
    
    Args:
        extracted_text: Văn bản đã được trích xuất
    
    Returns:
        Thông tin về các thực thể được phát hiện
    """
    
    name_pattern = r'(?:name|tên|họ tên)[:\s]*([A-Za-z\s]+)'
    address_pattern = r'(?:address|địa chỉ)[:\s]*([^,\n]+)'
    id_pattern = r'(?:id|number|số)[:\s]*([A-Z0-9]+)'
    
    names = re.findall(name_pattern, extracted_text, re.IGNORECASE)
    addresses = re.findall(address_pattern, extracted_text, re.IGNORECASE)
    ids = re.findall(id_pattern, extracted_text, re.IGNORECASE)
    
    names = list(set([name.strip() for name in names if len(name.strip()) > 2]))
    addresses = list(set([addr.strip() for addr in addresses if len(addr.strip()) > 5]))
    ids = list(set([id_num.strip() for id_num in ids if len(id_num.strip()) > 3]))
    
    result = f"""👥 MULTIPLE ENTITIES ANALYSIS
    
📊 Detected entities:
"""
    
    if len(names) > 1:
        result += f"👤 Names ({len(names)}):\n"
        for i, name in enumerate(names, 1):
            result += f"   {i}. {name}\n"
    
    if len(addresses) > 1:
        result += f"🏠 Addresses ({len(addresses)}):\n"
        for i, addr in enumerate(addresses, 1):
            result += f"   {i}. {addr}\n"
    
    if len(ids) > 1:
        result += f"🆔 ID Numbers ({len(ids)}):\n"
        for i, id_num in enumerate(ids, 1):
            result += f"   {i}. {id_num}\n"
    
    total_entities = len(names) + len(addresses) + len(ids)
    
    if total_entities > 3:
        result += f"""
⚠️ MULTIPLE ENTITIES DETECTED:
- Có thể là tài liệu gia đình hoặc nhóm
- Cần xác định thực thể chính
- Kiểm tra mối quan hệ giữa các thực thể

💡 RECOMMENDATION:
- Sử dụng thực thể đầu tiên làm chính
- Lưu trữ các thực thể khác như thông tin phụ
"""
    else:
        result += "\n✅ Số lượng thực thể trong mức bình thường"
    
    result += "\n✅ Entity analysis completed!"
    
    return result

def create_classify_agent():
    """
    Tạo Classification Agent với tất cả các tools
    
    Returns:
        Agent: Classification agent đã được cấu hình
    """
    classify_agent = Agent(
        model=bedrock_model,
        name="document_classifier",
        tools=[classify_document_type, extract_key_fields, detect_multiple_documents, handle_multiple_entities],
        system_prompt="""Bạn là chuyên gia phân loại và trích xuất dữ liệu từ tài liệu.

Nhiệm vụ của bạn:
1. Phân loại tài liệu theo 3 category: Identity, Address, Eligibility
2. Xác định tên cụ thể của giấy tờ (Driver's License, Passport, v.v.)
3. Trích xuất các trường dữ liệu quan trọng
4. Xử lý edge cases: nhiều tài liệu, nhiều thực thể

Quy trình làm việc:
1. Sử dụng classify_document_type để phân loại
2. Sử dụng extract_key_fields để trích xuất dữ liệu
3. Sử dụng detect_multiple_documents nếu nghi ngờ có nhiều tài liệu
4. Sử dụng handle_multiple_entities nếu phát hiện nhiều thực thể

Luôn trả lời bằng tiếng Việt, chi tiết và chính xác."""
    )
    return classify_agent

