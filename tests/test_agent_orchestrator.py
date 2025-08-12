"""Test Agent Orchestrator with Agents as Tools pattern"""

import sys
import os
import boto3
import logging
from strands_tools import retrieve, http_request
from strands import Agent, tool
from strands.models import BedrockModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    print("✅ Strands tools imported")
except ImportError:
    print("⚠️ Some strands tools not available, using mock")
    @tool
    def retrieve(query: str) -> str:
        return f"Retrieved information about: {query}"
    
    @tool
    def http_request(url: str) -> str:
        return f"HTTP request to: {url}"

logging.basicConfig(level=logging.INFO)

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

RESEARCH_ASSISTANT_PROMPT = """Bạn là trợ lý nghiên cứu chuyên nghiệp. Tập trung vào việc cung cấp
thông tin chính xác, có nguồn gốc rõ ràng để trả lời các câu hỏi nghiên cứu.
Luôn trích dẫn nguồn khi có thể và nghiên cứu kỹ lưỡng. Trả lời bằng tiếng Việt."""

PRODUCT_RECOMMENDATION_PROMPT = """Bạn là trợ lý tư vấn sản phẩm chuyên nghiệp.
Đưa ra gợi ý sản phẩm phù hợp dựa trên sở thích, ngân sách và nhu cầu của người dùng.
Xem xét các yếu tố như chất lượng, giá cả, đánh giá và yêu cầu của người dùng. Trả lời bằng tiếng Việt."""

TRIP_PLANNING_PROMPT = """Bạn là trợ lý lập kế hoạch du lịch chuyên nghiệp.
Tạo lịch trình du lịch chi tiết dựa trên sở thích, ngân sách và điểm đến của người dùng.
Bao gồm gợi ý về chỗ ở, hoạt động, nhà hàng và phương tiện di chuyển. Trả lời bằng tiếng Việt."""

@tool
def research_assistant(query: str) -> str:
    """Xử lý và trả lời các câu hỏi liên quan đến nghiên cứu.
    
    Args:
        query: Câu hỏi nghiên cứu cần thông tin chính xác
        
    Returns:
        Câu trả lời nghiên cứu chi tiết có trích dẫn
    """
    try:
        research_agent = Agent(
            model=bedrock_model,
            system_prompt=RESEARCH_ASSISTANT_PROMPT,
            tools=[retrieve, http_request]  
        )
        
        response = research_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Lỗi trong trợ lý nghiên cứu: {str(e)}"


@tool
def product_recommendation_assistant(query: str) -> str:
    """Xử lý các câu hỏi tư vấn sản phẩm bằng cách gợi ý sản phẩm phù hợp.
    
    Args:
        query: Câu hỏi về sản phẩm với sở thích của người dùng
        
    Returns:
        Gợi ý sản phẩm cá nhân hóa với lý do
    """
    try:
        product_agent = Agent(
            model=bedrock_model,
            system_prompt=PRODUCT_RECOMMENDATION_PROMPT,
            tools=[retrieve, http_request]  
        )
        
        response = product_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Lỗi trong tư vấn sản phẩm: {str(e)}"


@tool
def trip_planning_assistant(query: str) -> str:
    """Tạo lịch trình du lịch và cung cấp lời khuyên du lịch.
    
    Args:
        query: Yêu cầu lập kế hoạch du lịch với điểm đến và sở thích
        
    Returns:
        Lịch trình du lịch chi tiết hoặc lời khuyên du lịch
    """
    try:
        travel_agent = Agent(
            model=bedrock_model,
            system_prompt=TRIP_PLANNING_PROMPT,
            tools=[retrieve, http_request]  
        )
        
        response = travel_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Lỗi trong lập kế hoạch du lịch: {str(e)}"


MAIN_SYSTEM_PROMPT = """Bạn là trợ lý thông minh điều phối các truy vấn đến các agent chuyên biệt:

- Đối với câu hỏi nghiên cứu và thông tin thực tế → Sử dụng công cụ research_assistant
- Đối với tư vấn sản phẩm và mua sắm → Sử dụng công cụ product_recommendation_assistant  
- Đối với lập kế hoạch du lịch và lịch trình → Sử dụng công cụ trip_planning_assistant
- Đối với câu hỏi đơn giản không cần kiến thức chuyên môn → Trả lời trực tiếp

Luôn chọn công cụ phù hợp nhất dựa trên truy vấn của người dùng. Nếu không chắc chắn, hãy yêu cầu làm rõ.
Trả lời bằng tiếng Việt."""

orchestrator = Agent(
    model=bedrock_model,
    system_prompt=MAIN_SYSTEM_PROMPT,
    tools=[research_assistant, product_recommendation_assistant, trip_planning_assistant],
    callback_handler=None
)

def test_orchestrator():
    """Test the main orchestrator agent"""
    print("\n=== Test Orchestrator Agent ===")
    
    test_queries = [
        "AWS Cloud là gì?",  # Nên sử dụng research_assistant
        "Tư vấn các dịch vụ",  # Nên sử dụng product_recommendation
        "Lập kế hoạch sử dụng EC2",  # Nên sử dụng trip_planning
        "2+2 bằng bao nhiêu?",  # Nên trả lời trực tiếp
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n{'='*60}")
            print(f"Query {i}/{len(test_queries)}: {query}")
            print('='*60)
            
            response = orchestrator(query)
            print(f"\n📝 Response: {str(response)[:300]}...")
            
        except Exception as e:
            print(f"❌ Error with query '{query}': {e}")
    
    # In tóm tắt tool usage
    print("\n" + "="*60)
    print("✅ Orchestrator test completed!")

def main():
    """Main function to run all tests"""
    print("=" * 60)
    
    print(f"Model: {config.CHATBOT_AGENT_MODEL}")
    print(f"Region: {config.AWS_REGION}")
    print(f"Temperature: {config.BEDROCK_TEMPERATURE}")

    test_orchestrator()
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()