"""Claude integration with AWS Bedrock"""

import json
import logging
from typing import Dict, Any, Optional, List
from .session import AWSSession, create_aws_session_from_env
import config

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Claude models on AWS Bedrock"""
    
    def __init__(self, aws_session: Optional[AWSSession] = None):
        """
        Initialize Claude client
        
        Args:
            aws_session: AWS session object. If None, will create from environment
        """
        self.aws_session = aws_session or create_aws_session_from_env()
        self.bedrock_runtime = self.aws_session.get_bedrock_runtime_client()
        self.default_model = config.CHATBOT_AGENT_MODEL
    
    def chat(
        self,
        message: str,
        model_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Send a chat message to Claude
        
        Args:
            message: User message
            model_id: Claude model ID (default from config)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            system_prompt: System prompt for Claude
            conversation_history: Previous conversation messages
        
        Returns:
            str: Claude's response
        """
        try:
            # Use defaults from config if not provided
            model_id = model_id or self.default_model
            max_tokens = max_tokens or config.BEDROCK_MAX_TOKENS
            temperature = temperature or config.BEDROCK_TEMPERATURE
            
            # Build messages array
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Prepare request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            # Add system prompt if provided
            if system_prompt:
                body["system"] = system_prompt
            
            logger.info(f"Sending request to Claude model: {model_id}")
            
            # Call Bedrock
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                logger.error(f"Unexpected response format: {response_body}")
                return "Error: Unexpected response format from Claude"
                
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return f"Error: {str(e)}"
    
    def chat_with_context(
        self,
        message: str,
        context: str,
        model_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Chat with Claude providing additional context
        
        Args:
            message: User message
            context: Additional context for the conversation
            model_id: Claude model ID
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
        
        Returns:
            str: Claude's response
        """
        system_prompt = f"Context: {context}\n\nPlease respond based on the provided context."
        
        return self.chat(
            message=message,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt
        )
    
    def generate_response(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate a response from Claude (simple prompt completion)
        
        Args:
            prompt: Input prompt
            model_id: Claude model ID
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
        
        Returns:
            str: Generated response
        """
        return self.chat(
            message=prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature
        )


# Convenience functions
def chat_with_claude(
    message: str,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    system_prompt: Optional[str] = None
) -> str:
    """
    Quick function to chat with Claude
    
    Args:
        message: User message
        model_id: Claude model ID
        max_tokens: Maximum tokens to generate
        temperature: Temperature for response generation
        system_prompt: System prompt for Claude
    
    Returns:
        str: Claude's response
    """
    client = ClaudeClient()
    return client.chat(
        message=message,
        model_id=model_id,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system_prompt
    )

