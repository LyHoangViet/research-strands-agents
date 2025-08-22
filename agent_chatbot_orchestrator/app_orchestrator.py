"""Streamlit UI for Agent Orchestrator with Enhanced Streaming"""

import streamlit as st
import sys
import os
import uuid
import asyncio
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_chatbot_orchestrator.orchestrator_agent import orchestrator

def initialize_session():
    """Initialize session state variables"""
    if 'sessions' not in st.session_state:
        st.session_state.sessions = {}
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'step_by_step_mode' not in st.session_state:
        st.session_state.step_by_step_mode = True

def create_new_session():
    """Create a new chat session"""
    session_id = str(uuid.uuid4())[:8]
    st.session_state.sessions[session_id] = {
        'messages': [],
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'title': f"Session {session_id}"
    }
    st.session_state.current_session_id = session_id
    return session_id

def get_current_session():
    """Get current session or create new one if none exists"""
    if not st.session_state.current_session_id or st.session_state.current_session_id not in st.session_state.sessions:
        create_new_session()
    return st.session_state.sessions[st.session_state.current_session_id]

def add_message_to_session(role, content, steps=None, metrics=None):
    """Add message to current session"""
    session = get_current_session()
    message = {
        'role': role,
        'content': content,
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'steps': steps or [],
        'metrics': metrics
    }
    session['messages'].append(message)

def display_message(message):
    """Display a chat message with optional steps and metrics"""
    with st.chat_message(message['role']):
        st.write(message['content'])
        
        # Show timestamp
        st.caption(f"⏰ {message['timestamp']}")
        
        # Show steps if available and step-by-step mode is enabled
        if message.get('steps') and st.session_state.step_by_step_mode:
            with st.expander("🔍 Chi tiết các bước thực hiện", expanded=False):
                for i, step in enumerate(message['steps'], 1):
                    st.write(f"**Bước {i}:** {step}")
        
        # Show metrics if available
        if message.get('metrics') and st.session_state.get('show_metrics', False):
            with st.expander("📊 Thống kê performance", expanded=False):
                metrics = message['metrics']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Input Tokens", metrics.get('inputTokens', 0))
                with col2:
                    st.metric("Output Tokens", metrics.get('outputTokens', 0))
                with col3:
                    st.metric("Latency (ms)", metrics.get('latencyMs', 0))

def extract_content_from_response(response_data):
    """Extract content from complex Strands response structure"""
    try:
        # Handle different response structures based on your logs
        if isinstance(response_data, dict):
            # Case 1: Direct message structure
            if 'message' in response_data:
                message = response_data['message']
                if isinstance(message, dict) and 'content' in message:
                    content_list = message['content']
                    if isinstance(content_list, list) and len(content_list) > 0:
                        return content_list[0].get('text', str(response_data))
            
            # Case 2: Result structure
            if 'result' in response_data:
                result = response_data['result']
                if hasattr(result, 'message'):
                    message = result.message
                    if isinstance(message, dict) and 'content' in message:
                        content_list = message['content']
                        if isinstance(content_list, list) and len(content_list) > 0:
                            return content_list[0].get('text', str(response_data))
            
            # Case 3: Direct content
            if 'content' in response_data:
                return response_data['content']
        
        # If it has a message attribute (AgentResult object)
        if hasattr(response_data, 'message'):
            message = response_data.message
            if isinstance(message, dict) and 'content' in message:
                content_list = message['content']
                if isinstance(content_list, list) and len(content_list) > 0:
                    return content_list[0].get('text', str(response_data))
        
        # Fallback to string representation
        return str(response_data)
        
    except Exception as e:
        st.error(f"Error extracting content: {e}")
        return str(response_data)

def extract_metrics_from_response(response_data):
    """Extract metrics from Strands response"""
    try:
        if isinstance(response_data, dict):
            if 'result' in response_data:
                result = response_data['result']
                if hasattr(result, 'metrics'):
                    metrics = result.metrics
                    return {
                        'inputTokens': getattr(metrics, 'accumulated_usage', {}).get('inputTokens', 0),
                        'outputTokens': getattr(metrics, 'accumulated_usage', {}).get('outputTokens', 0),
                        'totalTokens': getattr(metrics, 'accumulated_usage', {}).get('totalTokens', 0),
                        'latencyMs': getattr(metrics, 'accumulated_metrics', {}).get('latencyMs', 0),
                        'toolCalls': len(getattr(metrics, 'tool_metrics', {}))
                    }
        
        if hasattr(response_data, 'metrics'):
            metrics = response_data.metrics
            return {
                'inputTokens': getattr(metrics, 'accumulated_usage', {}).get('inputTokens', 0),
                'outputTokens': getattr(metrics, 'accumulated_usage', {}).get('outputTokens', 0),
                'totalTokens': getattr(metrics, 'accumulated_usage', {}).get('totalTokens', 0),
                'latencyMs': getattr(metrics, 'accumulated_metrics', {}).get('latencyMs', 0),
                'toolCalls': len(getattr(metrics, 'tool_metrics', {}))
            }
        
        return None
    except Exception:
        return None

async def process_streaming_response(prompt):
    """Process streaming response from orchestrator"""
    try:
        agent_stream = orchestrator.stream_async(prompt)
        
        response_parts = []
        steps = ["🚀 Bắt đầu xử lý câu hỏi"]
        current_content = ""
        
        async for event in agent_stream:
            try:
                # Extract content from various event types
                content = extract_content_from_response(event)
                
                if content and content != str(event):
                    # This is actual content
                    current_content = content
                    steps.append("✅ Nhận được phản hồi từ agent")
                    
                    yield {
                        'type': 'content',
                        'data': content,
                        'steps': steps.copy(),
                        'metrics': extract_metrics_from_response(event)
                    }
                else:
                    # This might be a tool call or other event
                    if 'get_account_agent' in str(event):
                        steps.append("🔧 Đang gọi Account Agent...")
                    elif 'get_architect_agent' in str(event):
                        steps.append("🏗️ Đang gọi Architect Agent...")
                    elif 'get_docs_agent' in str(event):
                        steps.append("📚 Đang gọi Documentation Agent...")
                    
                    yield {
                        'type': 'step',
                        'data': f"Processing: {type(event).__name__}",
                        'steps': steps.copy(),
                        'metrics': extract_metrics_from_response(event)
                    }
            
            except Exception as e:
                steps.append(f"⚠️ Lỗi khi xử lý event: {str(e)}")
                yield {
                    'type': 'error',
                    'data': f"Event processing error: {e}",
                    'steps': steps.copy()
                }
        
        # Final response
        if current_content:
            steps.append("🎉 Hoàn thành xử lý")
            yield {
                'type': 'complete',
                'data': current_content,
                'steps': steps,
                'metrics': None
            }
        else:
            yield {
                'type': 'error',
                'data': "Không nhận được phản hồi từ agent",
                'steps': steps
            }
        
    except Exception as e:
        yield {
            'type': 'error',
            'data': f"❌ Lỗi streaming: {str(e)}",
            'steps': [f"❌ Lỗi: {str(e)}"]
        }

def main():
    st.set_page_config(
        page_title="AWS Agent Orchestrator",
        page_icon="🤖",
        layout="wide"
    )
    
    initialize_session()
    
    with st.sidebar:
        st.title("🗂️ Quản lý Session")
        
        if st.button("➕ Tạo Session Mới", use_container_width=True):
            create_new_session()
            st.rerun()
        
        if st.session_state.sessions:
            session_options = {
                session_id: f"{data['title']} ({data['created_at']})"
                for session_id, data in st.session_state.sessions.items()
            }
            
            selected_session = st.selectbox(
                "Chọn Session:",
                options=list(session_options.keys()),
                format_func=lambda x: session_options[x],
                index=list(session_options.keys()).index(st.session_state.current_session_id) if st.session_state.current_session_id in session_options else 0
            )
            
            if selected_session != st.session_state.current_session_id:
                st.session_state.current_session_id = selected_session
                st.rerun()
        
        st.divider()
        
        st.subheader("⚙️ Cài đặt")
        st.session_state.step_by_step_mode = st.checkbox(
            "Hiển thị từng bước", 
            value=st.session_state.step_by_step_mode,
            help="Hiển thị chi tiết các bước thực hiện khi agent gọi tools"
        )
        
        st.session_state.use_streaming = st.checkbox(
            "Chế độ streaming", 
            value=st.session_state.get('use_streaming', True),
            help="Sử dụng streaming để hiển thị phản hồi theo thời gian thực"
        )
        
        st.session_state.show_metrics = st.checkbox(
            "Hiển thị metrics",
            value=st.session_state.get('show_metrics', False),
            help="Hiển thị thống kê về tokens và performance"
        )
        
        if st.session_state.sessions and len(st.session_state.sessions) > 1:
            st.divider()
            if st.button("🗑️ Xóa Session Hiện Tại", use_container_width=True):
                if st.session_state.current_session_id in st.session_state.sessions:
                    del st.session_state.sessions[st.session_state.current_session_id]
                    if st.session_state.sessions:
                        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
                    else:
                        st.session_state.current_session_id = None
                    st.rerun()
    
    st.title("🤖 AWS Agent Orchestrator")
    st.markdown("Trợ lý thông minh cho AWS - Hỏi đáp về tài khoản, kiến trúc và tài liệu")
    
    if st.session_state.current_session_id:
        current_session = get_current_session()
        st.info(f"📝 Session hiện tại: {current_session['title']} - Tạo lúc: {current_session['created_at']}")
    
    # Display chat history
    current_session = get_current_session()
    for message in current_session['messages']:
        display_message(message)
    
    # Chat input
    if prompt := st.chat_input("Nhập câu hỏi về AWS..."):
        # Add user message
        add_message_to_session("user", prompt)
        
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        # Process response
        with st.chat_message("assistant"):
            try:
                use_streaming = st.session_state.get('use_streaming', True)
                
                if use_streaming:
                    # Streaming approach
                    response_placeholder = st.empty()
                    steps_placeholder = st.empty()
                    metrics_placeholder = st.empty()
                    
                    final_response = ""
                    final_steps = []
                    final_metrics = None
                    
                    async def handle_streaming():
                        nonlocal final_response, final_steps, final_metrics
                        
                        try:
                            # Show initial loading
                            response_placeholder.write("🔄 Đang xử lý...")
                            
                            async for event in process_streaming_response(prompt):
                                if event['type'] == 'content':
                                    final_response = event['data']
                                    response_placeholder.write(final_response)
                                    
                                    if event.get('steps') and st.session_state.step_by_step_mode:
                                        with steps_placeholder.expander("🔍 Chi tiết các bước thực hiện", expanded=True):
                                            for i, step in enumerate(event['steps'], 1):
                                                st.write(f"**{i}.** {step}")
                                
                                elif event['type'] == 'step':
                                    if st.session_state.step_by_step_mode and event.get('steps'):
                                        with steps_placeholder.expander("🔍 Chi tiết các bước thực hiện", expanded=True):
                                            for i, step in enumerate(event['steps'], 1):
                                                st.write(f"**{i}.** {step}")
                                
                                elif event['type'] == 'complete':
                                    final_response = event['data']
                                    final_steps = event['steps']
                                    final_metrics = event.get('metrics')
                                    response_placeholder.write(final_response)
                                    
                                elif event['type'] == 'error':
                                    response_placeholder.error(event['data'])
                                    final_response = event['data']
                                    final_steps = event.get('steps', [])
                            
                            # Clear loading message if still there
                            if final_response != "🔄 Đang xử lý...":
                                response_placeholder.write(final_response)
                            
                        except Exception as e:
                            error_msg = f"❌ Lỗi streaming: {str(e)}"
                            response_placeholder.error(error_msg)
                            final_response = error_msg
                    
                    # Run streaming
                    asyncio.run(handle_streaming())
                    
                else:
                    # Regular (non-streaming) approach
                    with st.spinner("Đang xử lý..."):
                        response = orchestrator(prompt)
                        
                        # Extract content from response
                        final_response = extract_content_from_response(response)
                        final_metrics = extract_metrics_from_response(response)
                        
                        st.write(final_response)
                        final_steps = [
                            "🔍 Phân tích câu hỏi của người dùng",
                            "🎯 Xác định agent phù hợp nhất", 
                            "🔧 Gọi tool tương ứng",
                            "✅ Xử lý kết quả và tạo phản hồi"
                        ] if st.session_state.step_by_step_mode else []
                
                # Show timestamp
                st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
                
                # Show final steps
                if final_steps and st.session_state.step_by_step_mode:
                    with st.expander("🔍 Chi tiết các bước thực hiện", expanded=False):
                        for i, step in enumerate(final_steps, 1):
                            st.write(f"**{i}.** {step}")
                
                # Show metrics
                if final_metrics and st.session_state.show_metrics:
                    with st.expander("📊 Thống kê performance", expanded=False):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Input Tokens", final_metrics.get('inputTokens', 0))
                        with col2:
                            st.metric("Output Tokens", final_metrics.get('outputTokens', 0))
                        with col3:
                            st.metric("Latency (ms)", final_metrics.get('latencyMs', 0))
                        with col4:
                            st.metric("Tool Calls", final_metrics.get('toolCalls', 0))
                
                # Add to session
                add_message_to_session("assistant", final_response, final_steps, final_metrics)
                
            except Exception as e:
                error_msg = f"❌ Lỗi: {str(e)}"
                st.error(error_msg)
                st.error(f"Chi tiết lỗi: {type(e).__name__}")
                add_message_to_session("assistant", error_msg)

if __name__ == "__main__":
    main()