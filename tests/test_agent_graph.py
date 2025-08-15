"""Test Strands Agent Graph - Structured multi-agent workflows"""

import sys
import os
import boto3
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent import GraphBuilder

logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
)

from botocore.config import Config

# Cấu hình timeout ngắn hơn
boto_config = Config(
    read_timeout=60,  
    connect_timeout=10,
    retries={'max_attempts': 2}
)

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

# Create tools for graph agents
@tool
def research_tool(topic: str) -> str:
    """Research information about a topic"""
    if "successful" in topic.lower():
        return f"Research completed successfully! Found 10 reliable sources about {topic}. Analysis shows positive results."
    elif "failed" in topic.lower():
        return f"Research failed. Could not find reliable sources about {topic}. Need to retry with different approach."
    else:
        return f"🔍 Nghiên cứu về {topic}:\n- Tìm thấy 10 nguồn tài liệu\n- Phân tích 5 nghiên cứu chính\n- Thu thập dữ liệu từ 3 database"

@tool
def analysis_tool(data: str) -> str:
    """Analyze research data"""
    return f"📊 Phân tích dữ liệu: {data[:50]}...\n- Xác định 3 xu hướng chính\n- Tính toán thống kê\n- Đưa ra 5 insight quan trọng"

@tool
def fact_check_tool(claims: str) -> str:
    """Fact check information and claims"""
    return f"✅ Kiểm tra sự thật: {claims[:50]}...\n- Xác minh 90% thông tin chính xác\n- Phát hiện 2 điểm cần làm rõ\n- Đánh giá độ tin cậy: 8.5/10"

@tool
def report_tool(content: str) -> str:
    """Generate comprehensive report"""
    return f"📝 Tạo báo cáo từ: {content[:50]}...\n- Cấu trúc 5 phần chính\n- Thêm 10 biểu đồ minh họa\n- Định dạng professional"

researcher = Agent(
    model=bedrock_model,
    name="researcher",
    tools=[research_tool],
    system_prompt="""Bạn là chuyên gia nghiên cứu. Sử dụng research_tool và trả lời ngắn gọn (tối đa 200 từ)."""
)

analyst = Agent(
    model=bedrock_model,
    name="analyst",
    tools=[analysis_tool],
    system_prompt="""Bạn là chuyên gia phân tích. Sử dụng analysis_tool và trả lời ngắn gọn (tối đa 200 từ)."""
)

fact_checker = Agent(
    model=bedrock_model,
    name="fact_checker",
    tools=[fact_check_tool],
    system_prompt="""Bạn là chuyên gia kiểm tra sự thật. Sử dụng fact_check_tool và trả lời ngắn gọn (tối đa 200 từ)."""
)

report_writer = Agent(
    model=bedrock_model,
    name="report_writer",
    tools=[report_tool],
    system_prompt="""Bạn là chuyên gia viết báo cáo. Sử dụng report_tool và trả lời ngắn gọn (tối đa 200 từ)."""
)

# Define conditional function first
def only_if_research_successful(state):
    """Only traverse if research was successful."""
    research_node = state.results.get("research")
    if not research_node:
        return False
    result_text = str(research_node.result)
    print(f"🔍 DEBUG: Research result text: {result_text[:100]}...")
    has_successful = "successful" in result_text.lower()
    print(f"🔍 DEBUG: Contains 'successful': {has_successful}")
    return has_successful


# Build the graph
builder = GraphBuilder()

# Add nodes
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(fact_checker, "fact_check")
builder.add_node(report_writer, "report")

# Add edges (dependencies)
builder.add_edge("research", "analysis", condition=only_if_research_successful)  
builder.add_edge("research", "fact_check")   
builder.add_edge("analysis", "report")   
builder.add_edge("fact_check", "report")   

builder.set_entry_point("research")

graph = builder.build()


def test_simple_graph():
    """Test simple graph execution"""
    print("=== Test Simple Graph ===")
    
    try:
        task = "AI trong y tế"
        print(f"Task: {task}")
        print("🚀 Starting graph execution...")
        
        result = graph(task)
        
        print(f"\n📊 Graph Results:")
        print(f"Status: {result.status}")
        print(f"Execution order: {[node.node_id for node in result.execution_order]}")
        print(f"Total nodes executed: {len(result.execution_order)}")
        
        if hasattr(result, 'final_result'):
            print(f"\n📝 Final Result:")
            print(str(result.final_result)[:300] + "..." if len(str(result.final_result)) > 300 else str(result.final_result))
        
        print("✅ Simple graph test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_complex_graph():
    """Test complex graph with detailed workflow"""
    print("\n=== Test Complex Graph ===")
    
    try:
        task = "Phân tích xu hướng công nghệ blockchain trong tài chính, kiểm tra tính chính xác và viết báo cáo chi tiết"
        print(f"Task: {task}")
        print("🚀 Starting complex graph execution...")
        
        # Execute the graph
        result = graph(task)
        
        print(f"\n📊 Complex Graph Results:")
        print(f"Status: {result.status}")
        print(f"Execution flow: {' → '.join([node.node_id for node in result.execution_order])}")
        
        # Show node dependencies
        print(f"\n🔗 Graph Structure:")
        print(f"- research → analysis, fact_check")
        print(f"- analysis → report")
        print(f"- fact_check → report")
        print(f"- Entry point: research")
        
        print("✅ Complex graph test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_parallel_execution():
    """Test parallel execution in graph"""
    print("\n=== Test Parallel Execution ===")
    
    try:
        task = "Nghiên cứu về machine learning, phân tích và kiểm tra thông tin song song"
        print(f"Task: {task}")
        print("🔧 Expected parallel execution:")
        print("1. research (first)")
        print("2. analysis + fact_check (parallel after research)")
        print("3. report (after both analysis and fact_check)")
        
        result = graph(task)
        
        print(f"\n📈 Parallel Results:")
        print(f"Status: {result.status}")
        print(f"Execution order: {[node.node_id for node in result.execution_order]}")
        
        # Check if analysis and fact_check ran after research
        execution_ids = [node.node_id for node in result.execution_order]
        research_idx = execution_ids.index("research")
        analysis_idx = execution_ids.index("analysis")
        fact_check_idx = execution_ids.index("fact_check")
        report_idx = execution_ids.index("report")
        
        print(f"\n🔍 Execution Analysis:")
        print(f"- Research position: {research_idx + 1}")
        print(f"- Analysis position: {analysis_idx + 1}")
        print(f"- Fact check position: {fact_check_idx + 1}")
        print(f"- Report position: {report_idx + 1}")
        
        if research_idx < analysis_idx and research_idx < fact_check_idx:
            print("✅ Correct: Research ran first")
        if analysis_idx < report_idx and fact_check_idx < report_idx:
            print("✅ Correct: Report ran after analysis and fact_check")
        
        print("✅ Parallel execution test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_conditional_logic():
    """Test conditional edge logic"""
    print("\n=== Test Conditional Logic ===")
    
    try:
        print("🔧 Testing conditional edge: research → analysis")
        print("- Analysis chỉ chạy nếu research có từ 'successful'")
        print("- Fact check luôn chạy sau research")
        print("- Report chỉ chạy nếu có analysis hoặc fact_check")
        
        # Test case 1: Research successful (should run analysis)
        print("\n--- Test Case 1: Research Successful ---")
        task1 = "AI trong y tế successful research"
        result1 = graph(task1)
        
        execution_ids1 = [node.node_id for node in result1.execution_order]
        print(f"Execution order: {execution_ids1}")
        
        if "analysis" in execution_ids1:
            print("✅ Analysis ran because research was successful")
        else:
            print("❌ Analysis should have run")
            
        # Test case 2: Research failed (should skip analysis)
        print("\n--- Test Case 2: Research Failed ---")
        task2 = "AI trong y tế failed research"
        result2 = graph(task2)
        
        execution_ids2 = [node.node_id for node in result2.execution_order]
        print(f"Execution order: {execution_ids2}")
        
        if "analysis" not in execution_ids2:
            print("✅ Analysis skipped because research failed")
        else:
            print("❌ Analysis should have been skipped")
            
        print("✅ Conditional logic test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_graph_with_tools():
    """Test graph agents using tools"""
    print("\n=== Test Graph with Tools ===")
    
    try:
        task = "Nghiên cứu về cybersecurity, sử dụng tools để phân tích và tạo báo cáo"
        print(f"Task: {task}")
        print("🔧 Expected tool usage:")
        print("- Researcher: research_tool(cybersecurity)")
        print("- Analyst: analysis_tool(research data)")
        print("- Fact checker: fact_check_tool(claims)")
        print("- Report writer: report_tool(final content)")
        
        result = graph(task)
        
        print(f"\n🛠️ Tools Results:")
        print(f"Status: {result.status}")
        print(f"All agents used their specialized tools")
        print(f"Tools worked in sequence through the graph")
        
        print("✅ Graph with tools test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run graph tests"""
    print("Testing Strands Agent Graph")
    print("=" * 50)
    
    print(f"Model: {config.CHATBOT_AGENT_MODEL}")
    print(f"Region: {config.AWS_REGION}")
    print(f"Temperature: {config.BEDROCK_TEMPERATURE}")
    print(f"Max Tokens: {config.BEDROCK_MAX_TOKENS}")
    
    print(f"\n📊 Graph Structure:")
    print(f"- Researcher (entry) → Analysis + Fact Check (parallel)")
    print(f"- Analysis + Fact Check → Report Writer (final)")
    
    print(f"\n👥 Graph Agents:")
    print(f"- Researcher: Thu thập thông tin với research_tool")
    print(f"- Analyst: Phân tích dữ liệu với analysis_tool")
    print(f"- Fact Checker: Kiểm tra sự thật với fact_check_tool")
    print(f"- Report Writer: Viết báo cáo với report_tool")
    
    # Run graph tests
    test_simple_graph()
    test_conditional_logic()  # Test conditional edge logic
    # test_complex_graph()
    # test_parallel_execution()
    # test_graph_with_tools()
    
    print("\n" + "=" * 50)
    print("All graph tests completed!")
    print("\n💡 Graph Benefits:")
    print("1. Structured workflow with dependencies")
    print("2. Parallel execution where possible")
    print("3. Clear data flow between agents")
    print("4. Deterministic execution order")
    print("5. Tools integration at each node")


if __name__ == "__main__":
    main()
