"""Test Agent Orchestrator with Agents as Tools pattern"""

import sys
import os
import boto3
import logging
import asyncio
from strands import Agent, tool
from strands.models import BedrockModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from agent_chatbot_orchestrator.agents.agent_account import account_agent
from agent_chatbot_orchestrator.agents.agent_architect import aws_architect_agent
from agent_chatbot_orchestrator.agents.agent_qa import aws_docs_agent

boto_session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config.AWS_SESSION_TOKEN,
    region_name=config.AWS_REGION
)

bedrock_model = BedrockModel(
    boto_session=boto_session,
    model_id=config.CHATBOT_AGENT_MODEL,
    temperature=config.BEDROCK_TEMPERATURE,
    max_tokens=config.BEDROCK_MAX_TOKENS,
)

@tool  
def get_account_agent(user_input: str) -> str:
    """Get information about AWS account resources"""
    response = account_agent(user_input)
    return response

@tool
def get_architect_agent(user_input: str) -> str:
    """Get AWS architecture design and recommendations"""  
    response = architect_agent(user_input)
    return response

@tool
def get_docs_agent(user_input: str) -> str:
    """Search AWS documentation and guides"""
    response = docs_agent(user_input) 
    return response

MAIN_SYSTEM_PROMPT = """
Bạn là trợ lý thông minh điều phối các agent chuyên biệt cho AWS.

Khi người dùng hỏi:
- Về resources/account AWS → Sử dụng get_account_agent(user_input)
- Về thiết kế/kiến trúc → Sử dụng get_architect_agent(user_input)  
- Về tài liệu AWS → Sử dụng get_docs_agent(user_input)

QUAN TRỌNG: Luôn gọi tool phù hợp thay vì tự trả lời.
Trả lời bằng ngôn ngữ câu hỏi.
"""

orchestrator = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[get_account_agent, get_architect_agent, get_docs_agent],
    callback_handler=None
)

async def process_streaming_response(user_input: str):
    """Process user input with streaming response"""
    print(f"🚀 Đang xử lý câu hỏi: {user_input}")
    print("📡 Streaming response...")
    print("-" * 50)
    
    agent_stream = orchestrator.stream_async(user_input)
    full_response = ""
    
    async for event in agent_stream:
        # Print chunk for debugging
        print(f"📦 Chunk: {event}")
        full_response += str(event)
        yield event
    
    print("-" * 50)
    print(f"✅ Hoàn thành! Tổng độ dài response: {len(full_response)} ký tự")

# Sync wrapper for compatibility
def run_streaming_response(user_input: str):
    """Synchronous wrapper for streaming response"""
    return asyncio.run(process_streaming_response(user_input))

# Alternative: Collect all chunks and return
async def get_streaming_response_as_list(user_input: str):
    """Get streaming response as a list of chunks"""
    chunks = []
    agent_stream = orchestrator.stream_async(user_input)
    
    async for event in agent_stream:
        chunks.append(str(event))
    
    return chunks

# For testing
async def test_streaming():
    """Test streaming functionality"""
    test_question = "Account của tôi hiện tại ở region us-east-1 có những resource nào?"
    
    print("=== Testing Streaming Response ===")
    async for chunk in process_streaming_response(test_question):
        # Simulate UI processing each chunk
        await asyncio.sleep(0.1)  # Small delay to simulate UI rendering
        print(f"UI received: {chunk}")

if __name__ == "__main__":
    # Test streaming
    print("🧪 Testing streaming functionality...")
    asyncio.run(test_streaming())
    
    # Interactive mode with streaming
    print("\n" + "="*60)
    print("🎯 Interactive mode với streaming")
    print("="*60)
    
    while True:
        user_question = input("\n❓ Câu hỏi: ").strip()
        if user_question.lower() in ['quit', 'exit', 'q']:
            print("👋 Tạm biệt!")
            break
        
        if user_question:
            # Run streaming response
            asyncio.run(process_streaming_response(user_question))

# def main():
#     """Test Agent Account get resource on Cloud AWS"""
#     print("Nhập câu hỏi về AWS (hoặc 'quit' để thoát):")
    
#     while True:
#         try:
#             user_input = input("\n❓ Câu hỏi: ").strip()
            
#             if user_input.lower() in ['quit', 'exit', 'q', 'thoát']:
#                 print("👋 Tạm biệt!")
#                 break
                
#             if not user_input:
#                 continue
            
#             response = orchestrator(user_input)
#             print(f"\n💡 Trả lời:\n{response}")
            
#         except KeyboardInterrupt:
#             print("\n\n👋 Tạm biệt!")
#             break
#         except Exception as e:
#             print(f"\n❌ Lỗi: {str(e)}")

# if __name__ == "__main__":
#     main()
