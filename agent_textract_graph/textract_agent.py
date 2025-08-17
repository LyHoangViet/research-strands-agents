"""Textract Agent Graph - Document processing workflow"""

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
from strands.multiagent import GraphBuilder

from tools.textact_tool import create_textract_agent
from tools.classify_tool import create_classify_agent
from tools.format_tool import create_format_agent

logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

textract_agent = create_textract_agent()
classify_agent = create_classify_agent()
format_agent = create_format_agent()

builder = GraphBuilder()

builder.add_node(textract_agent, "textract")
builder.add_node(classify_agent, "classify")
builder.add_node(format_agent, "format")

builder.add_edge("textract", "classify")
builder.add_edge("classify", "format")

builder.set_entry_point("textract")

document_processing_graph = builder.build()

def process_document(file_path: str) -> dict:
    """
    Hàm chính để xử lý tài liệu qua graph
    
    Args:
        file_path: Đường dẫn đến file cần xử lý
    
    Returns:
        dict: Kết quả xử lý từ graph
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File không tồn tại: {file_path}"}
        
        print(f"\n🚀 Bắt đầu xử lý file: {os.path.basename(file_path)}")
        print("=" * 50)
        
        # Simply pass the file path as a text prompt
        prompt = f"Xử lý tài liệu từ file: {file_path}"
        result = document_processing_graph(prompt)
        
        print("\n✅ Hoàn thành xử lý!")
        print("=" * 50)
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Lỗi khi xử lý file: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
