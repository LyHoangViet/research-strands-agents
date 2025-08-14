import logging
from strands import tool

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
            tools=[retrieve]  
        )
        
        response = research_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Lỗi trong trợ lý nghiên cứu: {str(e)}"
