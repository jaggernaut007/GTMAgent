import json
import logging
import os
from datetime import datetime, timezone
from operator import add
from pathlib import Path
from typing import Dict, List, TypedDict, Annotated, Any, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Local imports
from utils.chat_utils import count_tokens, truncate_messages, add_timestamps

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
MAX_TOKENS = 4000  # Default max tokens for context window

# Define the state for our chat application
class ChatState(TypedDict):
    messages: Annotated[list[dict], add]

class ChatProcessor:
    def __init__(self, conversation_id: str = "default"):
        """Initialize the chat processor with a conversation ID.
        
        Args:
            conversation_id: Unique identifier for the conversation.
        """
        self.conversation_id = conversation_id
        self.logger = logging.getLogger(f"{__name__}.ChatProcessor.{conversation_id}")
        
        self.logger.info(f"Initializing ChatProcessor for conversation: {conversation_id}")
        
        try:
            # Initialize the LLM with GPT-4o-mini
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.6,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.logger.debug("LLM initialized successfully")
            
            self.workflow = self._build_workflow()
            self.logger.debug("Workflow built successfully")
            
            # Initialize empty chat history
            self.chat_history = []
            self.logger.info("Initialized with empty in-memory chat history")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChatProcessor: {str(e)}", exc_info=True)
            raise
    
    def _build_workflow(self):
        """Build the LangGraph workflow for chat processing."""
        # Define the graph
        workflow = StateGraph(ChatState)
        
        # Add the LLM node
        workflow.add_node("llm", self._call_llm)
        
        # Set the entry point and define the flow
        workflow.set_entry_point("llm")
        workflow.add_edge("llm", END)
        
        # Compile the workflow
        return workflow.compile()
    
    def _call_llm(self, state: ChatState) -> dict:
        """Call the LLM with the current conversation state."""
        try:
            self.logger.debug(f"Preparing to call LLM with {len(state['messages'])} messages")
            
            # Convert to LangChain message format
            messages = []
            for msg in state["messages"]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    messages.append(SystemMessage(content=msg["content"]))
            
            self.logger.debug(f"Sending {len(messages)} messages to LLM")
            start_time = datetime.now(timezone.utc)
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(
                f"LLM call completed in {processing_time:.2f}s. "
                f"Response length: {len(response.content)}"
            )
            
            # Return the response in the expected format
            return {"messages": [{"role": "assistant", "content": response.content}]}
            
        except Exception as e:
            self.logger.error(f"Error in _call_llm: {str(e)}", exc_info=True)
            raise
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Return empty list as we're not persisting history."""
        self.logger.debug("Using in-memory history (no persistence)")
        return []
    
    def _save_history(self) -> None:
        """No-op since we're not persisting history."""
        self.logger.debug("Skipping history save (in-memory only)")
    
    def clear_history(self) -> None:
        """Clear the current conversation history from memory."""
        msg_count = len(self.chat_history)
        self.chat_history = []
        self.logger.info(f"Cleared {msg_count} messages from in-memory history")
    
    def process_message(self, message: str) -> str:
        """
        Process a single message and return a response using LangGraph and GPT-4o-mini.
        
        Args:
            message: The user's message
            
        Returns:
            The assistant's response
        """
        self.logger.info(f"Processing new message (length: {len(message)})")
        
        try:
            # Create user message with timestamp
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Add user message to history
            self.chat_history.append(user_message)
            self.logger.debug("Added user message to history")
            
            # Create a copy of the current history for processing
            processing_history = self.chat_history.copy()
            
            # Truncate history to fit token limit (leaving room for the response)
            before_truncate = len(processing_history)
            processing_history = truncate_messages(processing_history, MAX_TOKENS - 500)  # Reserve tokens for response
            
            if before_truncate != len(processing_history):
                self.logger.info(
                    f"Truncated history from {before_truncate} to {len(processing_history)} messages "
                    f"to fit token limit"
                )
            
            # Log token count
            total_tokens = sum(count_tokens(msg.get("content", "")) for msg in processing_history)
            self.logger.debug(f"Current processing token count: {total_tokens}")
            
            # Run the workflow with the processing history
            self.logger.debug("Invoking workflow...")
            start_time = datetime.now(timezone.utc)
            result = self.workflow.invoke({"messages": processing_history})
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Extract assistant's response
            response = result["messages"][-1]["content"]
            self.logger.debug(
                f"Generated response (length: {len(response)}) in {processing_time:.2f}s"
            )
            
            # Add assistant's response to the actual history
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.chat_history.append(assistant_message)
            
            # Log final state (no save needed for in-memory)
            final_token_count = sum(count_tokens(msg.get("content", "")) for msg in self.chat_history)
            self.logger.debug(f"Current in-memory token count: {final_token_count}")
            
            return response
                
        except Exception as e:
            self.logger.error(f"Error in process_message: {str(e)}", exc_info=True)
            raise

class ChatManager:
    """Manages multiple chat conversations."""
    
    def __init__(self):
        self.conversations: Dict[str, ChatProcessor] = {}
        self.logger = logging.getLogger(f"{__name__}.ChatManager")
        self.logger.info("Initializing ChatManager")
    
    def get_processor(self, conversation_id: str = "default") -> ChatProcessor:
        """Get or create a chat processor for the given conversation ID."""
        if conversation_id not in self.conversations:
            self.logger.info(f"Creating new ChatProcessor for conversation: {conversation_id}")
            self.conversations[conversation_id] = ChatProcessor(conversation_id)
            self.logger.info(f"Total active conversations: {len(self.conversations)}")
        else:
            self.logger.debug(f"Returning existing ChatProcessor for conversation: {conversation_id}")
        return self.conversations[conversation_id]
    
    async def clear_conversation(self, conversation_id: str) -> None:
        """Clear a specific conversation."""
        if conversation_id in self.conversations:
            self.logger.info(f"Clearing conversation: {conversation_id}")
            try:
                # Clear the conversation history
                self.conversations[conversation_id].clear_history()
                # Remove the conversation from the manager
                self.conversations.pop(conversation_id, None)
                self.logger.info(f"Successfully cleared conversation: {conversation_id}")
            except Exception as e:
                self.logger.error(f"Error clearing conversation {conversation_id}: {str(e)}", exc_info=True)
                raise
        else:
            self.logger.warning(f"Attempted to clear non-existent conversation: {conversation_id}")

# Global chat manager
chat_manager = ChatManager()
logger = logging.getLogger(__name__)

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

async def clear_conversation(conversation_id: str = "default") -> None:
    """Clear a conversation's history.
    
    Args:
        conversation_id: ID of the conversation to clear (defaults to "default")
    """
    try:
        logger.info(f"Request to clear conversation: {conversation_id}")
        await chat_manager.clear_conversation(conversation_id)
        logger.info(f"Successfully cleared conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"Error clearing conversation {conversation_id}: {str(e)}", exc_info=True)
        raise
