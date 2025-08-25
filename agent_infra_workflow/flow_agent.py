"""Test Strands Agent Workflow - Multi-agent workflow management"""
import sys
import os
import boto3
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

from strands import Agent
from strands.models import BedrockModel
from strands_tools import workflow

try:
    print("✅ Workflow tool imported")
except ImportError:
    print("⚠️ Workflow tool not available")
    workflow = None

logging.basicConfig(level=logging.INFO)

boto_session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    aws_session_token=config.AWS_SESSION_TOKEN,
    region_name=config.AWS_REGION
)

# Create Bedrock model
bedrock_model = BedrockModel(
    boto_session=boto_session,
    model_id=config.CHATBOT_AGENT_MODEL,
    temperature=config.BEDROCK_TEMPERATURE,
    max_tokens=config.BEDROCK_MAX_TOKENS,
)

# Create specialized agents
researcher = Agent(
    model=bedrock_model,
    system_prompt="You are a research specialist. Find key information.",
    callback_handler=None
)

analyst = Agent(
    model=bedrock_model,
    system_prompt="You analyze research data and extract insights.",
    callback_handler=None
)

writer = Agent(
    model=bedrock_model,
    system_prompt="You create polished reports based on analysis."
)

workflow_agent = Agent(
    model=bedrock_model,
    name="Workflow Agent",
    description="An agent that can create and manage multi-agent workflows.",
    tools=[workflow],
    callback_handler=None
)

def process_workflow(topic):
    """Process workflow with topic parameter"""
    research_results = researcher(f"Research the latest developments in {topic}")
    
    analysis = analyst(f"Analyze these research findings: {research_results}")
    
    final_report = writer(f"Create a report based on this analysis: {analysis}")
    
    return final_report


def test_sequential_workflow():
    """Test sequential workflow with topic"""
    print("=== Test Sequential Workflow ===")
    
    try:
        topic = "AI in healthcare"
        print(f"Processing topic: {topic}")
        
        final_report = process_workflow(topic)
        print("✅ Sequential workflow completed")
        print(f"Report preview: {str(final_report)[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_create_workflow():
    """Test creating a multi-agent workflow with workflow tool"""
    print("\n=== Test Create Workflow Tool ===")
    
    try:
        create_response = workflow_agent.tool.workflow(
            action="create",
            workflow_id="data_analysis",
            tasks=[
                {
                    "task_id": "data_extraction",
                    "description": "Extract key financial data from the quarterly report",
                    "system_prompt": "You extract and structure financial data from reports.",
                    "priority": 5
                },
                {
                    "task_id": "trend_analysis", 
                    "description": "Analyze trends in the data compared to previous quarters",
                    "dependencies": ["data_extraction"],
                    "system_prompt": "You identify trends in financial time series.",
                    "priority": 3
                },
                {
                    "task_id": "report_generation",
                    "description": "Generate a comprehensive analysis report", 
                    "dependencies": ["trend_analysis"],
                    "system_prompt": "You create clear financial analysis reports.",
                    "priority": 2
                }
            ]
        )
        
        print("✅ Workflow tool created successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_execute_workflow():
    """Test executing the workflow"""
    print("\n=== Test Execute Workflow Tool ===")
    
    try:
        start_response = workflow_agent.tool.workflow(action="start", workflow_id="data_analysis")
        print("✅ Workflow tool started")
        
        status_response = workflow_agent.tool.workflow(action="status", workflow_id="data_analysis")
        print("✅ Status checked")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_workflow_management():
    """Test workflow management operations"""
    print("\n=== Test Workflow Management ===")
    
    try:
        agent.tool.workflow(action="list")
        print("✅ Listed workflows")
        
        agent.tool.workflow(action="details", workflow_id="data_analysis")
        print("✅ Got workflow details")
        
        agent.tool.workflow(action="pause", workflow_id="data_analysis")
        print("✅ Paused workflow")
        
        agent.tool.workflow(action="resume", workflow_id="data_analysis")
        print("✅ Resumed workflow")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_pause_resume_workflow():
    """Test pause and resume workflow functionality"""
    print("\n=== Test Pause and Resume ===")
    
    try:
        pause_response = agent.tool.workflow(action="pause", workflow_id="data_analysis")
        if 'not yet implemented' in str(pause_response):
            print("⚠️ Pause not implemented")
        else:
            print("✅ Paused workflow")
        
        resume_response = agent.tool.workflow(action="resume", workflow_id="data_analysis")
        if 'not yet implemented' in str(resume_response):
            print("⚠️ Resume not implemented")
        else:
            print("✅ Resumed workflow")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_complex_workflow():
    """Test a more complex workflow with multiple dependencies"""
    print("\n=== Test Complex Workflow ===")
    
    try:
        agent.tool.workflow(
            action="create",
            workflow_id="simple_test",
            tasks=[
                {
                    "task_id": "task1",
                    "description": "First task",
                    "system_prompt": "You complete the first task.",
                    "priority": 3
                },
                {
                    "task_id": "task2", 
                    "description": "Second task",
                    "dependencies": ["task1"],
                    "system_prompt": "You complete the second task.",
                    "priority": 2
                }
            ]
        )
        print("✅ Complex workflow created")
        
        agent.tool.workflow(action="start", workflow_id="simple_test")
        print("✅ Complex workflow started")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function to run workflow tests"""
    print("Testing Strands Agent Workflow")
    print("=" * 40)
    
    print(f"Model: {config.CHATBOT_AGENT_MODEL}")
    print(f"Agents: researcher, analyst, writer, workflow_agent")
    
    test_sequential_workflow()  
    test_create_workflow()      
    test_execute_workflow()     
    
    print("\n" + "=" * 40)
    print("All workflow tests completed!")


if __name__ == "__main__":
    main()
