"""Streamlit UI for Amazon Textract Agent"""

import streamlit as st
import os
import sys
from PIL import Image
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.textact_tool import textract_tool
from textract_agent import process_document
from tools.classify_tool import classify_document_type, extract_key_fields
from tools.format_tool import create_final_json_output
import re

def main():
    st.set_page_config(
        page_title="Amazon Textract Agent",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Document Processing Pipeline")
    st.markdown("Xử lý tài liệu hoàn chỉnh: Textract → Classify → Format JSON")
    
    st.sidebar.header("🔧 Cấu hình")
    st.sidebar.info("""
    **Supported formats:**
    - PNG, JPEG, JPG
    - PDF (single page)
    
    **Max file size:** 10MB
    """)
    
    # Upload Section
    st.header("📤 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Chọn file hình ảnh hoặc PDF",
        type=['png', 'jpg', 'jpeg', 'pdf'],
        help="Kéo thả file vào đây hoặc click để chọn"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.success(f"✅ Đã upload: {uploaded_file.name}")
            st.info(f"📏 Kích thước: {uploaded_file.size / 1024:.1f} KB")
        
        with col2:
            if st.button("🔄 Process Document", type="primary", use_container_width=True):
                st.session_state.process_clicked = True
        
        # Image preview
        if uploaded_file.type.startswith('image'):
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Document Preview", width=400)
            except Exception as e:
                st.error(f"Không thể hiển thị ảnh: {e}")
    
    else:
        st.info("👆 Upload a document to start processing")
        
        st.subheader("📋 How it works")
        st.markdown("""
        **3-Step Pipeline:**
        1. 📄 **Extract** text from image/PDF
        2. 🏷️ **Classify** document type & extract fields  
        3. 📋 **Format** to structured JSON
        
        **Supported Documents:**
        - Identity: ID Card, Passport, Driver's License
        - Address: Utility Bill, Bank Statement
        - Eligibility: Certificate, Diploma
        """)
    
    # Processing Section
    if uploaded_file is not None and st.session_state.get('process_clicked', False):
        st.markdown("---")
        st.header("🚀 Processing Results")
        
        with st.spinner("Đang xử lý tài liệu..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_path = tmp_file.name
                
                # Run pipeline step by step and show results
                st.subheader("🔄 Processing Steps")
                
                # Step 1: Textract
                with st.status("📄 Step 1: Extracting text...", expanded=True) as status:
                    textract_result = textract_tool(temp_path)
                    st.text_area("Textract Output:", textract_result, height=200, key="textract_output")
                    status.update(label="✅ Step 1: Text extraction completed", state="complete")
                
                # Extract text for next steps
                extracted_text = ""
                if "NỘI DUNG:" in textract_result:
                    content_start = textract_result.find("NỘI DUNG:") + len("NỘI DUNG:")
                    content_end = textract_result.find("✅ Hoàn thành!")
                    if content_end == -1:
                        content_end = len(textract_result)
                    extracted_text = textract_result[content_start:content_end].strip()
                
                if extracted_text:
                    # Step 2: Classification
                    with st.status("🏷️ Step 2: Classifying document...", expanded=True) as status:
                        classification_result = classify_document_type(extracted_text)
                        st.text_area("Classification Output:", classification_result, height=200, key="classify_output")
                        status.update(label="✅ Step 2: Document classification completed", state="complete")
                    
                    # Extract category for field extraction
                    category = "Identity"  # Default
                    if "Category:" in classification_result:
                        category_match = re.search(r'Category:\s*([^\n]+)', classification_result)
                        if category_match:
                            category = category_match.group(1).strip()
                    
                    # Step 3: Field Extraction
                    with st.status("🔍 Step 3: Extracting fields...", expanded=True) as status:
                        extraction_result = extract_key_fields(extracted_text, category)
                        st.text_area("Field Extraction Output:", extraction_result, height=200, key="extract_output")
                        status.update(label="✅ Step 3: Field extraction completed", state="complete")
                    
                    # Step 4: JSON Formatting
                    with st.status("📋 Step 4: Formatting JSON...", expanded=True) as status:
                        final_json = create_final_json_output(
                            textract_result=textract_result,
                            classification_result=classification_result,
                            extraction_result=extraction_result
                        )
                        status.update(label="✅ Step 4: JSON formatting completed", state="complete")
                    
                    # Display Final JSON Result
                    st.markdown("---")
                    st.subheader("🎯 Final JSON Output")
                    
                    try:
                        import json
                        result_dict = json.loads(final_json)
                        
                        # Display formatted JSON
                        st.code(final_json, language="json")
                        
                        # Display summary metrics
                        st.subheader("📊 Summary")
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        with col_a:
                            st.metric("🏷️ Loại giấy tờ", result_dict.get('loai_giay_to', 'Unknown'))
                        
                        with col_b:
                            st.metric("📄 Tên giấy tờ", result_dict.get('ten_giay_to', 'Unknown'))
                        
                        with col_c:
                            fields_count = len(result_dict.get("cac_truong_du_lieu", {}))
                            st.metric("📝 Số trường", fields_count)
                        
                        with col_d:
                            warnings = result_dict.get("canh_bao_chat_luong_anh")
                            warning_count = len(warnings) if warnings else 0
                            st.metric("⚠️ Cảnh báo", warning_count)
                        
                        # Show extracted fields
                        if result_dict.get("cac_truong_du_lieu"):
                            st.subheader("🔍 Extracted Data")
                            for field, value in result_dict["cac_truong_du_lieu"].items():
                                st.text(f"• {field.replace('_', ' ').title()}: {value}")
                        
                        # Show warnings
                        if warnings:
                            st.subheader("⚠️ Warnings")
                            for warning in warnings:
                                st.warning(warning)
                    
                    except json.JSONDecodeError:
                        st.error("❌ Invalid JSON output")
                        st.text_area("Raw Output:", final_json, height=200)
                
                else:
                    st.error("❌ No text extracted from document")
                
                os.unlink(temp_path)
                
                # Reset the process button state
                st.session_state.process_clicked = False
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.process_clicked = False
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center'>
        <p>🔧 Powered by Amazon Textract & Strands Multi-Agent Framework</p>
        <p>📝 Document Processing Pipeline: Textract → Classify → Format</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()