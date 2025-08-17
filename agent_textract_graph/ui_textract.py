"""Streamlit UI for Textract Document Processing"""

import streamlit as st
import os
import json
import tempfile
from PIL import Image
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from textract_agent import process_document

def main():
    st.set_page_config(
        page_title="📄 Textract Document Processor",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Textract Document Processing System")
    st.markdown("---")
    
    with st.sidebar:
        st.header("🔧 Thông tin hệ thống")
        st.info("""
        **Quy trình xử lý:**
        1. 📸 Textract - Trích xuất văn bản
        2. 🏷️ Classify - Phân loại tài liệu  
        3. 📋 Format - Định dạng kết quả
        """)
        
        st.header("📁 Định dạng hỗ trợ")
        st.write("• JPG, JPEG")
        st.write("• PNG")
        st.write("• PDF")
    
    st.header("📤 Upload tài liệu")
    
    uploaded_file = st.file_uploader(
        "Chọn file tài liệu để xử lý",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Hỗ trợ các định dạng: JPG, PNG, PDF"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"✅ Đã tải file: {uploaded_file.name}")
            st.write(f"📊 Kích thước: {uploaded_file.size:,} bytes")
        
        with col2:
            process_button = st.button("🚀 Xử lý tài liệu", type="primary", use_container_width=True)
        
        if uploaded_file.type.startswith('image'):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Preview", use_container_width=True)
            except Exception as e:
                st.warning(f"Không thể hiển thị preview: {e}")
        
        # Process file when button clicked
        if process_button:
            process_uploaded_file(uploaded_file)
    
    st.markdown("---")
    
    st.header("📋 Kết quả xử lý")
    
    if 'processing_result' in st.session_state:
        display_results(st.session_state.processing_result)
    else:
        st.info("👆 Vui lòng upload và xử lý tài liệu để xem kết quả")

def process_uploaded_file(uploaded_file):
    """Process the uploaded file and display results"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("💾 Đang lưu file...")
        progress_bar.progress(25)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_file_path = tmp_file.name
        
        status_text.text("🔄 Đang xử lý tài liệu...")
        progress_bar.progress(50)
        
        result = process_document_safe(temp_file_path)
        
        progress_bar.progress(100)
        status_text.text("✅ Hoàn thành!")
        
        if isinstance(result, dict) and "error" in result:
            st.error(f"❌ Lỗi: {result['error']}")
        else:
            st.success("🎉 Xử lý thành công!")
            
            st.session_state.processing_result = result
            
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Lỗi không mong muốn: {str(e)}")
        
    finally:
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        progress_bar.empty()
        status_text.empty()

def process_document_safe(file_path: str) -> dict:
    """
    Process document using graph - return error if graph fails
    
    Args:
        file_path: Path to the file to process
    
    Returns:
        dict: Processing results or error
    """
    try:
        st.write("🔄 Đang xử lý qua graph...")
        result = process_document(file_path)
        
        return result
        
    except Exception as e:
        return {"error": f"❌ Lỗi graph: {str(e)}"}

def display_results(result):
    """Display processing results in a formatted way"""
    
    if hasattr(result, 'results') and hasattr(result, 'status'):
        final_result = None
        textract_content = ""
        classify_content = ""
        format_content = ""
        
        if 'textract' in result.results:
            textract_node = result.results['textract']
            if hasattr(textract_node, 'result') and hasattr(textract_node.result, 'message'):
                textract_content = textract_node.result.message['content'][0]['text']
        
        if 'classify' in result.results:
            classify_node = result.results['classify']
            if hasattr(classify_node, 'result') and hasattr(classify_node.result, 'message'):
                classify_content = classify_node.result.message['content'][0]['text']
        
        if 'format' in result.results:
            format_node = result.results['format']
            if hasattr(format_node, 'result') and hasattr(format_node.result, 'message'):
                format_content = format_node.result.message['content'][0]['text']
                
                import re
                
                json_patterns = [
                    r'```json\s*(\{[\s\S]*?\})\s*```',  
                    r'json\s*(\{[\s\S]*?\})',          
                    r'(\{[\s\S]*?"loai_giay_to"[\s\S]*?\})', 
                    r'(\{[^{}]*"loai_giay_to"[^{}]*\})' 
                ]
                
                for pattern in json_patterns:
                    json_match = re.search(pattern, format_content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        try:
                            json_str = json_str.strip()
                            brace_count = 0
                            clean_json = ""
                            for char in json_str:
                                clean_json += char
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        break
                            
                            final_result = json.loads(clean_json)
                            break
                        except Exception as e:
                            continue  
                
                if final_result is None:
                    st.warning("⚠️ Không thể parse JSON từ format agent, hiển thị raw content")
        
        result_dict = {
            "status": str(result.status),
            "execution_time": f"{result.execution_time/1000:.2f}s",
            "total_tokens": result.accumulated_usage.get('totalTokens', 0),
            "textract_content": textract_content,
            "classify_content": classify_content,
            "format_content": format_content,
            "final_result": final_result,
            "raw_result": str(result)[:1000] + "..." if len(str(result)) > 1000 else str(result)
        }
        result = result_dict
    
    tab1, tab2, tab3 = st.tabs(["📋 Tổng quan", "🔍 Chi tiết", "📊 JSON Raw"])
    
    with tab1:
        st.subheader("📋 Thông tin tổng quan")
        
        if isinstance(result, dict) and 'status' in result:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Status", result.get('status', 'N/A'))
            with col2:
                st.metric("⏱️ Execution Time", result.get('execution_time', 'N/A'))
            with col3:
                st.metric("🔤 Total Tokens", result.get('total_tokens', 'N/A'))
            
            if result.get('textract_content'):
                with st.expander("📸 Textract - Trích xuất văn bản"):
                    st.write(result['textract_content'])
            
            if result.get('classify_content'):
                with st.expander("🏷️ Classify - Phân loại tài liệu"):
                    st.write(result['classify_content'])
            
            if result.get('format_content'):
                with st.expander("📋 Format - Kết quả JSON"):
                    st.code(result['format_content'], language='json')
        else:
            if isinstance(result, dict):
                for key, value in result.items():
                    if key not in ["raw_data", "raw_result"]:
                        if isinstance(value, dict):
                            st.write(f"**{key}:**")
                            st.json(value)
                        else:
                            st.write(f"**{key}:** {str(value)[:500]}...")
            else:
                st.write(str(result))
    
    with tab2:
        st.subheader("🔍 Kết quả chi tiết")
        
        if isinstance(result, dict):
            for key, value in result.items():
                with st.expander(f"📂 {key}"):
                    if isinstance(value, (dict, list)):
                        st.json(value)
                    else:
                        st.write(value)
        else:
            st.text_area("Chi tiết:", value=str(result), height=300)
    
    with tab3:
        st.subheader("📊 Dữ liệu JSON Raw")
        
        try:
            if isinstance(result, dict):
                st.json(result)
            else:
                st.json({"result": str(result)})
        except:
            st.text_area("Raw data:", value=str(result), height=300)
    
    if isinstance(result, dict):
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        st.download_button(
            label="💾 Tải xuống kết quả (JSON)",
            data=json_str,
            file_name="textract_result.json",
            mime="application/json"
        )

def add_custom_css():
    st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    add_custom_css()
    main()