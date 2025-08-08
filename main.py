"""Main entry point for the Strands Agent Chatbot"""

import asyncio
from src.core.strands_manager import StrandsManager
from src.core.message_handler import MessageHandler
from src.agents.chatbot_agent import ChatbotAgent
from src.utils.config import Config
from src.utils.logger import setup_logger


async def main():
    """Main function to run the chatbot"""
    
    # Load configuration
    config = Config()
    
    # Setup logging
    logger = setup_logger(
        "chatbot",
        config.get("logging.file", "logs/chatbot.log"),
        config.get("logging.level", "INFO")
    )
    
    logger.info("Starting Strands Agent Chatbot...")
    
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
    
    logger.info(f"Registered agent: {chatbot.name}")
    
    # Simple console interface for testing
    print("Strands Agent Chatbot đã sẵn sàng!")
    print("Nhập 'quit' để thoát")
    
    while True:
        try:
            user_input = input("\nBạn: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'thoát']:
                break
            
            if user_input:
                response = await message_handler.handle_message(
                    user_input, 
                    "user_1"
                )
                print(f"Bot: {response}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            print(f"Lỗi: {e}")
    
    logger.info("Chatbot stopped")
    print("Tạm biệt!")


if __name__ == "__main__":
    asyncio.run(main())