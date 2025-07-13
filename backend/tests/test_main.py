import pytest

# Test the root endpoint
def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Startup Bakery API"}

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
