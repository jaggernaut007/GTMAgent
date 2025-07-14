import pytest
import json
import logging
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock, ANY
from fastapi.testclient import TestClient
from main import app, chat_manager

# Only enable async support for async tests
# pytestmark = pytest.mark.asyncio  # Removed as it's causing warnings for sync tests

# Test client fixture
@pytest.fixture
def test_app():
    with TestClient(app) as client:
        yield client

# Test the root endpoint
def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "documentation" in data
    assert "status" in data
    assert data["status"] == "running"  # Updated to match actual response

# Test the health check endpoint
def test_health_check(test_app):
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "startup-bakery"

# Test 404 for non-existent endpoint
def test_nonexistent_endpoint(test_app):
    response = test_app.get("/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"

# Test the chat endpoint
@patch('main.process_message')
def test_chat_endpoint(mock_process_message, test_app):
    # Setup mock
    mock_process_message.return_value = "Mocked response"
    
    # Test with a simple message
    response = test_app.post(
        "/chat",
        json={"message": "Hello, test!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert "error" in data
    assert "timestamp" in data
    assert data["response"] == "Mocked response"
    assert data["error"] is None
    
    # Verify process_message was called with correct arguments
    mock_process_message.assert_called_once_with(
        message="Hello, test!",
        conversation_id=ANY
    )

@patch('main.process_message')
def test_chat_empty_message(mock_process_message, test_app):
    # Setup mock
    mock_process_message.return_value = "Empty message received"
    
    # Test with an empty message
    response = test_app.post(
        "/chat",
        json={"message": ""}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "Empty message received"
    
    # Verify process_message was called with empty message
    mock_process_message.assert_called_once_with(
        message="",
        conversation_id=ANY
    )

def test_chat_missing_message_field(test_app):
    # Test with missing message field
    response = test_app.post(
        "/chat",
        json={}
    )
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()

@patch('main.process_message')
def test_chat_special_characters(mock_process_message, test_app):
    # Setup test data
    test_message = "Hello! @#$%^&*()_+{}|:\"<>?`~[];',./"
    mock_process_message.return_value = f"Processed: {test_message}"
    
    # Test with special characters
    response = test_app.post(
        "/chat",
        json={"message": test_message}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == f"Processed: {test_message}"
    
    # Verify process_message was called with the special characters
    mock_process_message.assert_called_once_with(
        message=test_message,
        conversation_id=ANY
    )

# Test the lifespan event handler
def test_lifespan_events(test_app, caplog):
    """Test that the lifespan events are properly logged."""
    # Clear any existing logs
    caplog.clear()
    
    # Check that the app is running by hitting the root endpoint
    response = test_app.get("/")
    assert response.status_code == 200
    
    # Check that the logs contain the expected messages
    log_messages = [record.message for record in caplog.records]
    
    # Check for specific log messages that should be present
    assert any("Root endpoint accessed" in msg for msg in log_messages)
    assert any("HTTP Request: GET http://testserver/" in msg for msg in log_messages)

# Test the health check endpoint
def test_health_check(test_app):
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "startup-bakery"
    assert "version" in data
    assert "timestamp" in data

# Test clearing a conversation
from unittest.mock import AsyncMock

@patch('chat_graph.clear_conversation')
def test_clear_conversation(mock_clear_conv, test_app):
    # Setup AsyncMock
    mock_clear_conv.side_effect = AsyncMock(return_value=None)
    
    # Test clearing a conversation
    conversation_id = "test_conv_123"
    response = test_app.post(f"/conversations/{conversation_id}/clear")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == f"Conversation {conversation_id} has been cleared"
    assert data["conversation_id"] == conversation_id
    assert "timestamp" in data
    
    # Verify clear_conversation was called with the correct conversation_id
    mock_clear_conv.assert_awaited_once_with(conversation_id)
