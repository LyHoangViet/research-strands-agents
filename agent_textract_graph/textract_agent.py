"""Textract Agent Graph - Document processing workflow"""

import sys
import os
import boto3
import logging
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder

from tools.textact_tool import create_textract_agent
from tools.classify_tool import create_classify_agent
from tools.format_tool import create_format_agent

logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)

def only_if_textract_successful(state):
    """Only proceed if textract was successful."""
    textract_node = state.results.get("textract")
    if not textract_node:
        return False
    result_text = str(textract_node.result)
    return "thành công" in result_text.lower() or "hoàn thành" in result_text.lower()

def only_if_classify_successful(state):
    """Only proceed if classification was successful."""
    classify_node = state.results.get("classify")
    if not classify_node:
        return False
    result_text = str(classify_node.result)
    success_indicators = [
        "completed", "hoàn thành", "phân loại", "classification", 
        "identity", "address", "eligibility", "category"
    ]
    return any(indicator in result_text.lower() for indicator in success_indicators)

textract_agent = create_textract_agent()
classify_agent = create_classify_agent()
format_agent = create_format_agent()

builder = GraphBuilder()

builder.add_node(textract_agent, "textract")
builder.add_node(classify_agent, "classify")
builder.add_node(format_agent, "format")

builder.add_edge("textract", "classify", condition=only_if_textract_successful)
builder.add_edge("classify", "format", condition=only_if_classify_successful)

builder.set_entry_point("textract")

document_processing_graph = builder.build()

def process_document(file_path: str) -> str:
    """
    Xử lý tài liệu qua toàn bộ pipeline
    
    Args:
        file_path: Đường dẫn đến file cần xử lý
    
    Returns:
        JSON kết quả cuối cùng hoặc kết quả từ bước cuối cùng
    """
    try:
        prompt = f"Xử lý tài liệu từ file: {file_path}"
        result = document_processing_graph(prompt)
        
        print(f"\n📊 PROCESSING COMPLETED")
        print(f"Status: {result.status}")
        print(f"Execution order: {[node.node_id for node in result.execution_order]}")
        
        if result.execution_order:
            last_node = result.execution_order[-1]
            return str(last_node.result)
        else:
            return "No nodes executed"
        
    except Exception as e:
        error_result = {
            "loai_giay_to": "Error",
            "ten_giay_to": "Processing Failed",
            "cac_truong_du_lieu": {},
            "canh_bao_chat_luong_anh": [f"Processing error: {str(e)}"]
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)
