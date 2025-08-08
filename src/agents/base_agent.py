"""Base agent class for Strands Agent framework"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.memory = []
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process incoming message and return response"""
        pass
    
    def add_to_memory(self, message: str, response: str):
        """Add conversation to memory"""
        self.memory.append({
            "message": message,
            "response": response,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()