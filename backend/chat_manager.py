from services.chatgraph_service import ChatProcessor
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ChatManager:
    """Manages multiple chat conversations."""
    def __init__(self):
        self.conversations: Dict[str, ChatProcessor] = {}
        self.logger = logging.getLogger(f"{__name__}.ChatManager")
        self.logger.info("Initializing ChatManager")

    def get_processor(self, conversation_id: str = "default") -> ChatProcessor:
        if conversation_id not in self.conversations:
            self.logger.info(f"Creating new ChatProcessor for conversation: {conversation_id}")
            self.conversations[conversation_id] = ChatProcessor(conversation_id)
            self.logger.info(f"Total active conversations: {len(self.conversations)}")
        else:
            self.logger.debug(f"Returning existing ChatProcessor for conversation: {conversation_id}")
        return self.conversations[conversation_id]

    def clear_conversation(self, conversation_id: str = "default") -> None:
        if conversation_id in self.conversations:
            self.logger.info(f"Clearing conversation: {conversation_id}")
            try:
                self.conversations[conversation_id].clear_history()
                self.conversations.pop(conversation_id, None)
                self.logger.info(f"Successfully cleared conversation: {conversation_id}")
            except Exception as e:
                self.logger.error(f"Error clearing conversation {conversation_id}: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.warning(f"Attempted to clear non-existent conversation: {conversation_id}")

chat_manager = ChatManager()

def process_message(message: str, conversation_id: str = "default") -> str:
    """
    Process a single message and return a response using LangGraph and GPT-4o-mini.
    Args:
        message: The user's message
        conversation_id: ID of the conversation (defaults to "default")
    Returns:
        The assistant's response
    """
    try:
        logger.info(f"Processing message for conversation: {conversation_id}")
        processor = chat_manager.get_processor(conversation_id)
        response = processor.process_message(message)
        logger.debug(f"Successfully processed message for conversation: {conversation_id}")
        return response
    except Exception as e:
        logger.error(f"Error in process_message for conversation {conversation_id}: {str(e)}", exc_info=True)
        raise

def clear_conversation(conversation_id: str = "default") -> None:
    """Clear a conversation's history.
    Args:
        conversation_id: ID of the conversation to clear (defaults to "default")
    """
    try:
        logger.info(f"Request to clear conversation: {conversation_id}")
        chat_manager.clear_conversation(conversation_id)
        logger.info(f"Successfully cleared conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"Error clearing conversation {conversation_id}: {str(e)}", exc_info=True)
        raise
