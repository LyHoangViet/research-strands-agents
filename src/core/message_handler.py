"""Message handling and routing"""

from typing import Dict, Any, Optional
from .strands_manager import StrandsManager


class MessageHandler:
    """Handles incoming messages and routes them appropriately"""
    
    def __init__(self, strands_manager: StrandsManager):
        self.strands_manager = strands_manager
        self.message_history = []
    
    async def handle_message(self, message: str, user_id: str, context: Dict[str, Any] = None) -> str:
        """Handle incoming message from user"""
        context = context or {}
        context["user_id"] = user_id
        
        # Get appropriate agent
        agent = self.strands_manager.get_agent("ChatbotAgent")
        if not agent:
            return "Agent not available"
        
        # Process message
        response = await agent.process_message(message, context)
        
        # Store in history
        self._store_message(user_id, message, response)
        
        return response
    
    def _store_message(self, user_id: str, message: str, response: str):
        """Store message in history"""
        self.message_history.append({
            "user_id": user_id,
            "message": message,
            "response": response,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()