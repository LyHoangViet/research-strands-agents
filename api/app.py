"""FastAPI application for the chatbot"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio

from src.core.strands_manager import StrandsManager
from src.core.message_handler import MessageHandler
from src.agents.chatbot_agent import ChatbotAgent
from src.utils.config import Config
from src.utils.logger import setup_logger


# Pydantic models
class MessageRequest(BaseModel):
    message: str
    user_id: str
    context: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str


# Initialize FastAPI app
app = FastAPI(
    title="Strands Agent Chatbot API",
    description="API cho chatbot sử dụng Strands Agent framework",
    version="1.0.0"
)

# Global variables
strands_manager = None
message_handler = None
logger = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global strands_manager, message_handler, logger
    
    # Load configuration
    config = Config()
    
    # Setup logging
    logger = setup_logger(
        "chatbot_api",
        config.get("logging.file", "logs/chatbot_api.log"),
        config.get("logging.level", "INFO")
    )
    
    logger.info("Starting Strands Agent Chatbot API...")
    
    # Initialize components
    strands_manager = StrandsManager()
    message_handler = MessageHandler(strands_manager)
    
    # Create and register chatbot agent
    agent_config = config.get("agent", {})
    chatbot = ChatbotAgent(
        name=agent_config.get("name", "ChatbotAgent"),
        config=agent_config
    )
    strands_manager.register_agent(chatbot)
    
    logger.info(f"API initialized with agent: {chatbot.name}")


@app.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest):
    """Process chat message"""
    try:
        response = await message_handler.handle_message(
            request.message,
            request.user_id,
            request.context
        )
        
        from datetime import datetime
        return MessageResponse(
            response=response,
            user_id=request.user_id,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Strands Agent Chatbot"}


@app.get("/agents")
async def list_agents():
    """List registered agents"""
    if strands_manager:
        return {"agents": list(strands_manager.agents.keys())}
    return {"agents": []}


if __name__ == "__main__":
    import uvicorn
    config = Config()
    uvicorn.run(
        app,
        host=config.get("api.host", "localhost"),
        port=config.get("api.port", 8000),
        reload=config.get("api.debug", True)
    )