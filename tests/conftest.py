import os
import pytest
from unittest.mock import MagicMock

# Set environment variables BEFORE any ursa_dsp imports
os.environ["GEMINI_API_KEY"] = "fake_key_for_testing"


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    monkeypatch.setenv("ENV_PATH", ".env.test")


@pytest.fixture
def mock_genai(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"section_content": "Mocked Content"}'

    mock_client.models.generate_content.return_value = mock_response

    # Mock the Client constructor to return our mock_client instance
    monkeypatch.setattr("google.genai.Client", MagicMock(return_value=mock_client))

    return mock_client
