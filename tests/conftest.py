import os
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("ENV_PATH", ".env.test")

@pytest.fixture
def mock_genai(monkeypatch):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"section_content": "Mocked Content"}'
    mock_model.generate_content.return_value = mock_response
    
    mock_configure = MagicMock()
    
    monkeypatch.setattr("google.generativeai.GenerativeModel", MagicMock(return_value=mock_model))
    monkeypatch.setattr("google.generativeai.configure", mock_configure)
    
    return mock_model
