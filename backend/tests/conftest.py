import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as test_client:
        yield test_client
