"""Test Strands Agent Swarm - Multi-agent collaboration"""

import sys
import os
import boto3
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import Swarm
from strands import tool
from strands_tools.calculator import calculator

logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()],
    level=logging.INFO
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
    temperature=config.BEDROCK_TEMPERATURE,
    max_tokens=config.BEDROCK_MAX_TOKENS,
)

# Try to import calculator tool
try:
    print("✅ Calculator tool imported")
except ImportError:
    print("⚠️ Calculator tool not available, creating mock")
    @tool
    def calculator(expression: str) -> str:
        """Calculate mathematical expressions"""
        try:
            result = eval(expression)
            return f"Kết quả: {expression} = {result}"
        except:
            return f"Không thể tính: {expression}"

# Create custom tools for different agents
@tool
def research_database(query: str) -> str:
    """Search research database for information"""
    return f"🔍 Tìm kiếm database: {query}\n📊 Kết quả: Tìm thấy 5 tài liệu về {query}\n📝 Thông tin chi tiết đã được thu thập"

@tool
def code_generator(specification: str) -> str:
    """Generate code based on specification"""
    return f"""💻 Tạo code cho: {specification}

```python
# Generated code for {specification}
def main():
    print("Implementation for {specification}")
    return True

if __name__ == "__main__":
    main()
```
✅ Code đã được generate thành công"""

@tool
def code_analyzer(code: str) -> str:
    """Analyze code for issues and improvements"""
    issues = [
        "⚠️ Thiếu error handling",
        "📝 Cần thêm docstring", 
        "⚡ Có thể optimize performance",
        "🔒 Cần kiểm tra security"
    ]
    return f"🔍 Phân tích code:\n" + "\n".join(issues) + "\n✅ Phân tích hoàn tất"

@tool
def architecture_planner(requirements: str) -> str:
    """Plan system architecture based on requirements"""
    return f"""🏗️ Kiến trúc hệ thống cho: {requirements}

📋 Kiến trúc đề xuất:
1. 🎨 Frontend: React/Vue.js
2. ⚙️ Backend: FastAPI/Django  
3. 🗄️ Database: PostgreSQL
4. 🚀 Cache: Redis
5. 📦 Deployment: Docker + Kubernetes

✅ Kiến trúc đã được thiết kế"""

# Create specialized agents with tools
researcher = Agent(
    model=bedrock_model,
    name="researcher",
    tools=[research_database, calculator],  # Research tools
    system_prompt="""Bạn là chuyên gia nghiên cứu với các tools:
- research_database: Tìm kiếm thông tin trong database
- calculator: Tính toán các con số

Nhiệm vụ của bạn là:
- Nghiên cứu và phân tích yêu cầu chi tiết
- Sử dụng tools để thu thập thông tin
- Đưa ra các khuyến nghị dựa trên nghiên cứu
- Chuyển giao công việc cho architect hoặc coder
Trả lời bằng tiếng Việt."""
)

coder = Agent(
    model=bedrock_model,
    name="coder",
    tools=[code_generator, calculator],  # Coding tools
    system_prompt="""Bạn là chuyên gia lập trình với các tools:
- code_generator: Tạo code từ specification
- calculator: Tính toán logic và algorithms

Nhiệm vụ của bạn là:
- Viết code chất lượng cao dựa trên yêu cầu
- Sử dụng tools để generate và tính toán
- Implement các tính năng được yêu cầu
- Chuyển giao cho reviewer để review code
Trả lời bằng tiếng Việt."""
)

reviewer = Agent(
    model=bedrock_model,
    name="reviewer",
    tools=[code_analyzer],  # Review tools
    system_prompt="""Bạn là chuyên gia review code với tools:
- code_analyzer: Phân tích code để tìm issues

Nhiệm vụ của bạn là:
- Review code về chất lượng, security, performance
- Sử dụng tools để analyze code
- Đưa ra feedback và gợi ý cải thiện
- Chuyển giao cho architect nếu cần thiết kế lại
Trả lời bằng tiếng Việt."""
)

architect = Agent(
    model=bedrock_model,
    name="architect",
    tools=[architecture_planner, calculator],  # Architecture tools
    system_prompt="""Bạn là chuyên gia kiến trúc hệ thống với tools:
- architecture_planner: Lập kế hoạch kiến trúc hệ thống
- calculator: Tính toán capacity và performance

Nhiệm vụ của bạn là:
- Thiết kế kiến trúc hệ thống tổng thể
- Sử dụng tools để plan và calculate
- Đưa ra các quyết định về công nghệ
- Hướng dẫn team về implementation
Trả lời bằng tiếng Việt."""
)

swarm = Swarm(
    [researcher, coder, reviewer, architect],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  
    node_timeout=300.0,       
    repetitive_handoff_detection_window=8,  
    repetitive_handoff_min_unique_agents=3
)


def test_simple_swarm_task():
    """Test swarm with a simple task"""
    print("=== Test Simple Swarm Task ===")
    
    try:
        task = "Tạo một ứng dụng calculator đơn giản bằng Python"
        print(f"Task: {task}")
        print("🚀 Starting swarm execution...")
        
        # Execute the swarm on a task
        result = swarm(task)
        
        # Access the final result
        print(f"\n📊 Swarm Results:")
        print(f"Status: {result.status}")
        print(f"Node history: {[node.node_id for node in result.node_history]}")
        print(f"Total nodes: {len(result.node_history)}")
        
        # Print final result
        if hasattr(result, 'final_result'):
            print(f"\n📝 Final Result:")
            print(str(result.final_result)[:500] + "..." if len(str(result.final_result)) > 500 else str(result.final_result))
        
        print("✅ Simple swarm task completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_complex_swarm_task():
    """Test swarm with a complex task"""
    print("\n=== Test Complex Swarm Task ===")
    
    try:
        task = "Thiết kế và implement một REST API đơn giản cho ứng dụng todo list với các tính năng CRUD"
        print(f"Task: {task}")
        print("🚀 Starting complex swarm execution...")
        
        # Execute the swarm on a complex task
        result = swarm(task)
        
        # Access the final result
        print(f"\n📊 Complex Swarm Results:")
        print(f"Status: {result.status}")
        print(f"Agent flow: {' → '.join([node.node_id for node in result.node_history])}")
        print(f"Total handoffs: {len(result.node_history) - 1}")
        
        # Show agent contributions
        agent_contributions = {}
        for node in result.node_history:
            agent_name = node.node_id
            if agent_name not in agent_contributions:
                agent_contributions[agent_name] = 0
            agent_contributions[agent_name] += 1
        
        print(f"\n👥 Agent Contributions:")
        for agent_name, count in agent_contributions.items():
            print(f"- {agent_name}: {count} lần tham gia")
        
        print("✅ Complex swarm task completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_swarm_with_tools():
    """Test swarm agents using tools in sequence"""
    print("\n=== Test Swarm with Tools ===")
    
    try:
        task = "Tạo một calculator app với 100 users, cần tính toán performance và thiết kế architecture"
        print(f"Task: {task}")
        print("🚀 Starting swarm with tools...")

        result = swarm(task)
        
        print(f"\n📊 Tools Usage Results:")
        print(f"Status: {result.status}")
        print(f"Agent flow: {' → '.join([node.node_id for node in result.node_history])}")
        
        # Show which agents used which tools
        print(f"\n🔧 Expected Tool Usage:")
        print(f"- Researcher: research_database (tìm info về calculator apps)")
        print(f"- Researcher: calculator (tính toán user requirements)")
        print(f"- Architect: architecture_planner (thiết kế hệ thống)")
        print(f"- Architect: calculator (tính performance cho 100 users)")
        print(f"- Coder: code_generator (tạo calculator code)")
        print(f"- Reviewer: code_analyzer (phân tích code quality)")
        
        print("✅ Swarm with tools test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_tools_chain_usage():
    """Test tools being used in chain across agents"""
    print("\n=== Test Tools Chain Usage ===")
    
    try:
        task = "Phân tích 50+30 users, thiết kế database cho họ, tạo code và review"
        print(f"Task: {task}")
        print("🔧 Expected tool chain:")
        print("1. Researcher: calculator(50+30) → research_database(user management)")
        print("2. Architect: calculator(80 users capacity) → architecture_planner(database)")
        print("3. Coder: code_generator(user management) → calculator(optimize)")
        print("4. Reviewer: code_analyzer(review code)")
        
        result = swarm(task)
        
        print(f"\n📈 Chain Results:")
        print(f"Status: {result.status}")
        print(f"Agents: {len(set(node.node_id for node in result.node_history))} unique agents")
        print(f"Total steps: {len(result.node_history)}")
        
        print("✅ Tools chain test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_swarm_collaboration():
    """Test specific swarm collaboration patterns"""
    print("\n=== Test Swarm Collaboration ===")
    
    collaboration_tasks = [
        "Phân tích yêu cầu cho một chatbot AI",
        "Code một function để xử lý authentication", 
        "Review và cải thiện performance của API"
    ]
    
    for i, task in enumerate(collaboration_tasks, 1):
        print(f"\n--- Collaboration Test {i}: {task} ---")
        
        try:
            result = swarm(task)
            print(f"✅ Task {i} completed")
            print(f"Agents involved: {set(node.node_id for node in result.node_history)}")
            
        except Exception as e:
            print(f"❌ Task {i} failed: {e}")


def main():
    """Main function to run swarm tests"""
    print("Testing Strands Agent Swarm")
    print("=" * 50)
    
    print(f"Model: {config.CHATBOT_AGENT_MODEL}")
    print(f"Region: {config.AWS_REGION}")
    print(f"Temperature: {config.BEDROCK_TEMPERATURE}")
    print(f"Max Tokens: {config.BEDROCK_MAX_TOKENS}")
    
    print(f"\n👥 Swarm Agents:")
    print(f"- Researcher: Nghiên cứu và phân tích")
    print(f"- Coder: Lập trình và implement")
    print(f"- Reviewer: Review code và quality")
    print(f"- Architect: Thiết kế kiến trúc")
    
    print(f"\n⚙️ Swarm Configuration:")
    print(f"- Max handoffs: 20")
    print(f"- Max iterations: 20")
    print(f"- Execution timeout: 15 minutes")
    print(f"- Node timeout: 5 minutes")
    
    # Run swarm tests
    # test_simple_swarm_task()
    # test_complex_swarm_task()
    test_swarm_with_tools()
    # test_tools_chain_usage()
    # test_swarm_collaboration()
    
    print("\n" + "=" * 50)
    print("All swarm tests completed!")
    print("\n💡 Swarm Benefits:")
    print("1. Multi-agent collaboration")
    print("2. Specialized expertise per agent")
    print("3. Automatic handoffs between agents")
    print("4. Complex task decomposition")
    print("5. Quality assurance through review")


if __name__ == "__main__":
    main()
