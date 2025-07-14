import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the functions and classes to test
import chat_graph
import main
from chat_graph import ChatProcessor, ChatManager, process_message, clear_conversation
from main import app

# Test client for FastAPI app
@pytest.fixture
def test_app():
    with TestClient(app) as test_client:
        yield test_client

# Fixture for a mock LLM response
@pytest.fixture
def mock_llm_response():
    class MockLLMResponse:
        def __init__(self, content):
            self.content = content
            self.response_metadata = {}
    
    return MockLLMResponse("Mocked LLM response")

# Test ChatProcessor class
class TestChatProcessor:
    @patch('chat_graph.ChatOpenAI')
    def test_chat_processor_initialization(self, mock_chat_openai):
        """Test that ChatProcessor initializes correctly."""
        conversation_id = "test_conversation"
        processor = ChatProcessor(conversation_id=conversation_id)
        
        assert processor.conversation_id == conversation_id
        assert processor.chat_history == []
        mock_chat_openai.assert_called_once()
    
    @patch('chat_graph.ChatOpenAI')
    def test_process_message(self, mock_chat_openai, mock_llm_response):
        """Test processing a message through the chat processor."""
        # Setup mock
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_llm_response
        mock_chat_openai.return_value = mock_llm
        
        # Initialize processor and process a message
        processor = ChatProcessor(conversation_id="test_conv")
        response = processor._call_llm({"messages": [{"role": "user", "content": "Hello!"}]})
        
        # Verify the response
        assert "messages" in response
        assert len(response["messages"]) == 1
        assert response["messages"][0]["role"] == "assistant"
        assert "content" in response["messages"][0]

# Test ChatManager class
class TestChatManager:
    def test_get_processor_new_conversation(self):
        """Test getting a processor for a new conversation."""
        manager = ChatManager()
        conversation_id = "new_conversation"
        
        with patch('chat_graph.ChatProcessor') as mock_chat_processor:
            # Set up the mock to return a processor with expected attributes
            mock_processor = MagicMock()
            mock_processor.chat_history = []
            mock_processor.created_at = datetime.now(timezone.utc).isoformat()
            mock_chat_processor.return_value = mock_processor
            
            processor = manager.get_processor(conversation_id)
            
            # Verify the processor was created and added to conversations
            mock_chat_processor.assert_called_once()
            assert conversation_id in manager.conversations
            assert manager.conversations[conversation_id] == mock_processor
    
    def test_get_processor_existing_conversation(self):
        """Test getting a processor for an existing conversation."""
        manager = ChatManager()
        conversation_id = "existing_conversation"
        
        # First call creates the processor
        with patch('chat_graph.ChatProcessor') as mock_chat_processor:
            manager.get_processor(conversation_id)
            mock_chat_processor.assert_called_once()
        
        # Second call should return the same processor without creating a new one
        with patch('chat_graph.ChatProcessor') as mock_chat_processor_again:
            manager.get_processor(conversation_id)
            mock_chat_processor_again.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_clear_conversation(self):
        """Test clearing a conversation."""
        manager = ChatManager()
        conversation_id = "to_clear"
        
        # Add a conversation
        with patch('chat_graph.ChatProcessor'):
            manager.get_processor(conversation_id)
            assert conversation_id in manager.conversations
            
            # Clear the conversation
            await manager.clear_conversation(conversation_id)
            assert conversation_id not in manager.conversations

# Test process_message function
def test_process_message_function():
    """Test the top-level process_message function."""
    # Create a mock processor that returns a simple string response
    mock_processor = MagicMock()
    mock_processor.process_message.return_value = "Mocked LLM response"
    
    # Create a mock chat manager
    mock_chat_manager = MagicMock()
    mock_chat_manager.get_processor.return_value = mock_processor
    
    # Patch the chat_manager in the chat_graph module
    with patch('chat_graph.chat_manager', mock_chat_manager), \
         patch('chat_graph.ChatOpenAI') as mock_chat_openai, \
         patch('chat_graph.datetime') as mock_datetime:
        
        # Setup mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        # Setup mock LLM response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Mocked LLM response")
        mock_chat_openai.return_value = mock_llm
        
        # Call the function
        response = process_message("Test message", "test_conv")
        
        # Verify the response
        assert response == "Mocked LLM response"
        mock_chat_manager.get_processor.assert_called_once_with("test_conv")
        mock_processor.process_message.assert_called_once_with("Test message")

# Test FastAPI integration
class TestChatEndpoints:
    def test_chat_endpoint_with_conversation_id(self, test_app):
        """Test the chat endpoint with a conversation ID."""
        # Create a mock processor that returns a simple string response
        mock_processor = MagicMock()
        
        # Create a mock LLM response with a string content attribute
        mock_llm_response = MagicMock()
        mock_llm_response.content = "Test response"
        
        # Set up the processor to return our mock LLM response
        mock_processor.process_message.return_value = mock_llm_response.content
        
        # Set up chat history with valid message format for token counting
        mock_processor.chat_history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Test response"}
        ]
        
        # Create a mock chat manager
        mock_chat_manager = MagicMock()
        mock_chat_manager.get_processor.return_value = mock_processor
        
        # Create a mock datetime object for the response
        mock_now = datetime.now(timezone.utc)
        
        # Patch the chat_manager in the main module and other dependencies
        with patch('main.chat_manager', mock_chat_manager), \
             patch('main.datetime') as mock_datetime, \
             patch('chat_graph.ChatOpenAI') as mock_chat_openai, \
             patch('chat_graph.count_tokens') as mock_count_tokens, \
             patch('chat_graph.chat_manager', mock_chat_manager):
            
            # Setup mock datetime
            mock_datetime.now.return_value = mock_now
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Mock token counting to return a fixed number
            mock_count_tokens.return_value = 10
            
            # Setup mock LLM to return our mock response
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = mock_llm_response
            mock_chat_openai.return_value = mock_llm
            
            # Make the request
            response = test_app.post(
                "/chat",
                json={"message": "Hello!"},
                headers={"X-Conversation-ID": "test_conv_123"}
            )
            
            # Verify the response
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
            data = response.json()
            assert "response" in data
            assert "conversation_id" in data
            assert "timestamp" in data
            assert data["conversation_id"] == "test_conv_123"
            assert data["response"] == "Test response"
            
            # Verify the processor was called
            mock_chat_manager.get_processor.assert_called_once_with("test_conv_123")
            mock_processor.process_message.assert_called_once_with("Hello!")
    
    @pytest.mark.asyncio
    async def test_clear_conversation_endpoint(self, test_app):
        """Test the clear conversation endpoint."""
        # Create a mock chat manager with an async clear_conversation method
        mock_chat_manager = AsyncMock()
        mock_chat_manager.clear_conversation.return_value = True
        
        # Create a mock datetime object for the response
        mock_now = datetime.now(timezone.utc)
        
        # Patch the chat_manager in the main module and chat_graph module
        with patch('main.chat_manager', mock_chat_manager), \
             patch('chat_graph.chat_manager', mock_chat_manager), \
             patch('main.datetime') as mock_datetime:
            
            # Setup mock datetime
            mock_datetime.now.return_value = mock_now
            mock_datetime.utcnow.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Make the request
            response = test_app.post(
                "/conversations/test_conv_123/clear"
            )
            
            # Verify the response
            assert response.status_code == 200, f"Expected status code 200, got {response.status_code}. Response: {response.text}"
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "conversation_id" in data
            assert data["conversation_id"] == "test_conv_123"
            assert "timestamp" in data
            
            # Verify the chat manager's clear_conversation was called
            mock_chat_manager.clear_conversation.assert_called_once_with("test_conv_123")
    
    def test_list_conversations_endpoint(self, test_app):
        """Test the list conversations endpoint."""
        with patch('main.chat_manager') as mock_chat_manager:
            # Setup mock
            mock_processor1 = MagicMock()
            mock_processor1.chat_history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
            mock_processor1.created_at = "2023-01-01T00:00:00"
            
            mock_processor2 = MagicMock()
            mock_processor2.chat_history = [
                {"role": "user", "content": "Test"}
            ]
            mock_processor2.created_at = "2023-01-02T00:00:00"
            
            mock_chat_manager.conversations = {
                "conv1": mock_processor1,
                "conv2": mock_processor2
            }
            
            # Make the request
            response = test_app.get("/conversations")
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            
            # Check that each conversation has the required fields
            for conv in data:
                assert "id" in conv
                assert "created_at" in conv
                assert "message_count" in conv
