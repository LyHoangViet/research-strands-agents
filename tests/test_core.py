"""Tests for core modules"""

import pytest
from src.core.strands_manager import StrandsManager
from src.agents.chatbot_agent import ChatbotAgent


class TestStrandsManager:
    """Test cases for StrandsManager"""
    
    @pytest.fixture
    def manager(self):
        """Create test manager"""
        return StrandsManager()
    
    @pytest.fixture
    def agent(self):
        """Create test agent"""
        return ChatbotAgent("TestAgent")
    
    def test_register_agent(self, manager, agent):
        """Test agent registration"""
        manager.register_agent(agent)
        
        assert "TestAgent" in manager.agents
        assert manager.get_agent("TestAgent") == agent
    
    def test_create_strand(self, manager):
        """Test strand creation"""
        strand_id = manager.create_strand(["TestAgent"])
        
        assert strand_id in manager.active_strands
        assert strand_id.startswith("strand_")