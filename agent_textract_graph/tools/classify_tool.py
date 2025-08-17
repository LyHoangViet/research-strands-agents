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
    Sử dụng LLM để phân loại loại giấy tờ dựa trên văn bản đã trích xuất
    
    Args:
        extracted_text: Văn bản đã được trích xuất từ Textract
    
    Returns:
        Kết quả phân loại với category và document type
    """
    
    classification_prompt = f"""
Bạn là chuyên gia phân loại tài liệu. Hãy phân loại tài liệu sau đây dựa trên nội dung văn bản:

VĂN BẢN TRÍCH XUẤT:
{extracted_text}

YÊU CẦU PHÂN LOẠI:
1. Category (chọn 1 trong 3):
   - Identity: Giấy tờ tùy thân (CCCD, CMND, Hộ chiếu, Bằng lái xe)
   - Address: Giấy tờ chứng minh địa chỉ (Hóa đơn điện nước, Sao kê ngân hàng, Hợp đồng thuê)
   - Eligibility: Giấy tờ chứng minh năng lực (Bằng cấp, Chứng chỉ, Giấy xác nhận thu nhập)

2. Document Type: Tên cụ thể của giấy tờ (VD: "Căn Cước Công Dân", "Hộ Chiếu", "Bằng Lái Xe")

3. Confidence Score: Mức độ tin cậy từ 1-10

ĐỊNH DẠNG TRẢ LỜI:
📋 DOCUMENT CLASSIFICATION

🏷️ Category: [Category]
📄 Document Type: [Document Type]
🎯 Confidence Score: [Score]/10
📝 Reasoning: [Lý do phân loại ngắn gọn]

✅ Classification completed!

LƯU Ý:
- Phân tích kỹ nội dung, không chỉ dựa vào từ khóa
- Xử lý được text có lỗi OCR hoặc không dấu
- Ưu tiên độ chính xác cao
"""
    
    return classification_prompt

@tool
def extract_key_fields(extracted_text: str, document_category: str) -> str:
    """
    Sử dụng LLM để trích xuất các trường dữ liệu quan trọng dựa trên loại tài liệu
    
    Args:
        extracted_text: Văn bản đã được trích xuất
        document_category: Loại tài liệu (Identity/Address/Eligibility)
    
    Returns:
        Các trường dữ liệu đã được trích xuất
    """
    
    extraction_prompt = f"""
Bạn là chuyên gia trích xuất dữ liệu từ tài liệu. Hãy trích xuất các trường dữ liệu quan trọng từ văn bản sau:

LOẠI TÀI LIỆU: {document_category}

VĂN BẢN TRÍCH XUẤT:
{extracted_text}

CÁC TRƯỜNG CẦN TRÍCH XUẤT:

Nếu là Identity (Giấy tờ tùy thân):
- Họ và tên (Full Name)
- Ngày sinh (Date of Birth) 
- Số CCCD/CMND/Hộ chiếu (ID Number)
- Địa chỉ thường trú (Address)
- Giới tính (Gender)
- Quê quán (Place of Origin)
- Ngày cấp (Issue Date)
- Nơi cấp (Issued By)

Nếu là Address (Chứng minh địa chỉ):
- Tên chủ hộ (Name)
- Địa chỉ (Address)
- Số điện thoại (Phone)
- Ngày hóa đơn (Bill Date)
- Số tiền (Amount)

Nếu là Eligibility (Chứng minh năng lực):
- Họ và tên (Full Name)
- Ngày sinh (Date of Birth)
- Tên bằng cấp/chứng chỉ (Certificate Name)
- Ngày cấp (Issue Date)
- Nơi cấp (Issued By)

ĐỊNH DẠNG TRẢ LỜI:
🔍 EXTRACTED KEY FIELDS ({document_category.upper()})

📝 [Tên trường]: [Giá trị]
📝 [Tên trường]: [Giá trị]
...

✅ Field extraction completed!

LƯU Ý:
- Chỉ trích xuất các trường có thông tin rõ ràng
- Xử lý được text có lỗi OCR hoặc không dấu
- Nếu không tìm thấy thông tin, ghi "Không có thông tin"
- Chuẩn hóa format ngày tháng về DD/MM/YYYY
"""
    
    return extraction_prompt

@tool
def detect_multiple_documents(extracted_text: str) -> str:
    """
    Sử dụng LLM để phát hiện và xử lý trường hợp một ảnh có nhiều loại giấy tờ
    
    Args:
        extracted_text: Văn bản đã được trích xuất
    
    Returns:
        Thông tin về các tài liệu được phát hiện
    """
    
    detection_prompt = f"""
Bạn là chuyên gia phân tích tài liệu. Hãy phân tích văn bản sau để phát hiện có bao nhiêu loại giấy tờ khác nhau:

VĂN BẢN TRÍCH XUẤT:
{extracted_text}

CÁC LOẠI TÀI LIỆU CÓ THỂ CÓ:
- Căn Cước Công Dân (CCCD)
- Chứng Minh Nhân Dân (CMND)  
- Hộ Chiếu (Passport)
- Bằng Lái Xe (Driver's License)
- Hóa Đơn Điện/Nước (Utility Bill)
- Sao Kê Ngân Hàng (Bank Statement)
- Hợp Đồng Thuê Nhà (Lease Agreement)
- Bằng Cấp/Chứng Chỉ (Certificate/Diploma)
- Giấy Xác Nhận Thu Nhập (Income Certificate)

NHIỆM VỤ:
1. Phân tích xem có bao nhiêu loại tài liệu khác nhau
2. Xác định tên cụ thể của từng loại
3. Đánh giá độ tin cậy cho mỗi loại (1-10)

ĐỊNH DẠNG TRẢ LỜI:

Nếu phát hiện NHIỀU tài liệu:
🔍 MULTIPLE DOCUMENTS DETECTED

📊 Found [số lượng] document types:
1. [Tên tài liệu 1] (confidence: [điểm]/10)
2. [Tên tài liệu 2] (confidence: [điểm]/10)

⚠️ RECOMMENDATION:
- Xử lý từng tài liệu riêng biệt
- Ưu tiên tài liệu có confidence cao nhất
- Kiểm tra lại kết quả trích xuất

✅ Multi-document detection completed!

Nếu chỉ có MỘT tài liệu:
📄 SINGLE DOCUMENT DETECTED

🏷️ Document Type: [Tên tài liệu]
🎯 Confidence: [điểm]/10

✅ Single document confirmed!

LƯU Ý:
- Chỉ coi là "multiple documents" khi thực sự có 2+ loại tài liệu khác nhau
- Không nhầm lẫn giữa thông tin trên cùng 1 tài liệu
- Xử lý được text có lỗi OCR
"""
    
    return detection_prompt

@tool
def handle_multiple_entities(extracted_text: str) -> str:
    """
    Sử dụng LLM để xử lý trường hợp một tài liệu có nhiều thực thể (người, địa chỉ, v.v.)
    
    Args:
        extracted_text: Văn bản đã được trích xuất
    
    Returns:
        Thông tin về các thực thể được phát hiện
    """
    
    entities_prompt = f"""
Bạn là chuyên gia phân tích thực thể trong tài liệu. Hãy phân tích văn bản sau để phát hiện có bao nhiêu thực thể khác nhau:

VĂN BẢN TRÍCH XUẤT:
{extracted_text}

CÁC LOẠI THỰC THỂ CẦN PHÂN TÍCH:
- Tên người (Names): Họ tên đầy đủ của các cá nhân
- Địa chỉ (Addresses): Các địa chỉ khác nhau (thường trú, tạm trú, nơi sinh)
- Số định danh (ID Numbers): CCCD, CMND, Hộ chiếu, v.v.
- Số điện thoại (Phone Numbers)
- Email addresses
- Ngày tháng (Dates): Ngày sinh, ngày cấp, v.v.

NHIỆM VỤ:
1. Xác định có bao nhiêu thực thể khác nhau cho mỗi loại
2. Liệt kê cụ thể từng thực thể
3. Phân tích xem có phải multiple entities hay không

ĐỊNH DẠNG TRẢ LỜI:

Nếu phát hiện NHIỀU thực thể:
👥 MULTIPLE ENTITIES ANALYSIS

📊 Detected entities:
👤 Names ([số lượng]):
   1. [Tên 1]
   2. [Tên 2]

🏠 Addresses ([số lượng]):
   1. [Địa chỉ 1]
   2. [Địa chỉ 2]

🆔 ID Numbers ([số lượng]):
   1. [ID 1]
   2. [ID 2]

⚠️ MULTIPLE ENTITIES DETECTED:
- Có thể là tài liệu gia đình hoặc nhóm
- Cần xác định thực thể chính
- Kiểm tra mối quan hệ giữa các thực thể

💡 RECOMMENDATION:
- Sử dụng thực thể đầu tiên làm chính
- Lưu trữ các thực thể khác như thông tin phụ

✅ Entity analysis completed!

Nếu chỉ có thực thể BÌNH THƯỜNG:
👥 SINGLE ENTITY ANALYSIS

📊 Detected entities:
👤 Names: [số lượng]
🏠 Addresses: [số lượng]  
🆔 ID Numbers: [số lượng]

✅ Số lượng thực thể trong mức bình thường

✅ Entity analysis completed!

LƯU Ý:
- Chỉ coi là "multiple entities" khi có 2+ thực thể cùng loại
- Phân biệt giữa thông tin chính và thông tin phụ
- Xử lý được text có lỗi OCR
"""
    
    return entities_prompt

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
    