"""Configuration management"""

import json
import os
from typing import Dict, Any


class Config:
    """Configuration manager for the chatbot"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "agent": {
                "name": "ChatbotAgent",
                "personality": "helpful",
                "max_memory": 100
            },
            "strands": {
                "max_active": 10,
                "timeout": 300
            },
            "logging": {
                "level": "INFO",
                "file": "logs/chatbot.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
    
    def save(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)