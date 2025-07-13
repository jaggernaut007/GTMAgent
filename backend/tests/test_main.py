import pytest
import json

# Test the root endpoint
def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Startup Bakery. Let's start baking some dough!"}

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
def test_chat_endpoint(test_app):
    # Test with a simple message
    response = test_app.post(
        "/chat",
        json={"message": "Hello, test!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "error" in data
    assert data["response"] == "You said: Hello, test!"
    assert data["error"] is None

def test_chat_empty_message(test_app):
    # Test with an empty message
    response = test_app.post(
        "/chat",
        json={"message": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "You said: "

def test_chat_missing_message_field(test_app):
    # Test with missing message field
    response = test_app.post(
        "/chat",
        json={}
    )
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()

def test_chat_special_characters(test_app):
    # Test with special characters
    test_message = "Hello! @#$%^&*()_+{}|:\"<>?`~[];',./"
    response = test_app.post(
        "/chat",
        json={"message": test_message}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == f"You said: {test_message}"
