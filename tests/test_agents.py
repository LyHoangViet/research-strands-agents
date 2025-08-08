from strands import Agent
from strands.models import BedrockModel

# Create a Bedrock model instance
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-premier-v1:0",
    temperature=0.3,
    top_p=0.8,
)

# Create an agent using the BedrockModel instance
agent = Agent(model=bedrock_model)

# Use the agent
response = agent("Tell me about Amazon Bedrock.")