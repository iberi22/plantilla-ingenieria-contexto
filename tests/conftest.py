import pytest
import os
import sys
from unittest.mock import MagicMock, Mock

# Mock whisper and TTS modules globally before any imports
# Create proper module mocks with required functions
whisper_mock = Mock()
whisper_mock.load_model = Mock()
sys.modules['whisper'] = whisper_mock

tts_module_mock = Mock()
tts_api_mock = Mock()
tts_api_mock.TTS = Mock()
sys.modules['TTS'] = tts_module_mock
sys.modules['TTS.api'] = tts_api_mock

# Mock transformers module for translation tests
transformers_mock = Mock()
transformers_mock.MarianMTModel = Mock()
transformers_mock.MarianTokenizer = Mock()
sys.modules['transformers'] = transformers_mock
sys.modules['transformers.tokenization_utils_fast'] = Mock()

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Set mock environment variables for all tests."""
    os.environ["GITHUB_TOKEN"] = "mock_github_token"
    os.environ["GOOGLE_API_KEY"] = "mock_google_api_key"
    os.environ["YOUTUBE_CLIENT_SECRET"] = "mock_client_secret.json"
    os.environ["YOUTUBE_REFRESH_TOKEN"] = "mock_refresh_token"

@pytest.fixture
def mock_repo_data():
    return {
        "name": "test-repo",
        "full_name": "user/test-repo",
        "description": "A test repository",
        "html_url": "https://github.com/user/test-repo",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "language": "Python",
        "stargazers_count": 100,
        "forks_count": 10
    }
