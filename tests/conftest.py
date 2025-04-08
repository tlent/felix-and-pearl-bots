import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'test'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AWS_REGION'] = 'us-east-1'  # Some AWS SDK versions use this
    os.environ['AWS_SESSION_TOKEN'] = 'test'
    os.environ['AWS_SECURITY_TOKEN'] = 'test'

@pytest.fixture(scope="session", autouse=True)
def app_env():
    """Set up application-specific environment variables."""
    env_vars = {
        'TEST_MODE': 'true',
        'ANTHROPIC_API_KEY': 'test_key',
        'FELIX_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'PEARL_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'WEATHER_API_KEY': 'test_weather_key',
        'WEATHER_LOCATION': 'Test City,TS,US',
        'BIRTHDAYS_CONFIG': json.dumps({
            "04-16": {"name": "Test Person"},
            "04-23": {"name": "Felix"},
            "04-21": {"name": "Pearl"}
        })
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    env_vars = {
        'ANTHROPIC_API_KEY': 'test-key',
        'FELIX_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'PEARL_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'WEATHER_API_KEY': 'test-key',
        'WEATHER_LOCATION': 'Test City,Test State,Test Country',
        'BIRTHDAYS_CONFIG': '{"04-16": {"name": "Felix"}}',
        'TEST_MODE': 'true'
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture(scope="function")
def mock_claude():
    """Mock Anthropic Claude API."""
    with patch('anthropic.Anthropic') as mock:
        mock.messages.create.return_value = MagicMock(content=[MagicMock(text="Test message")])
        yield mock

@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests library."""
    with patch('requests') as mock:
        mock.post.return_value = MagicMock(status_code=204)
        mock.get.return_value = MagicMock(text="<html></html>")
        yield mock

@pytest.fixture(scope="function")
def mock_send_discord():
    """Mock send_discord function."""
    with patch('app.send_message') as mock:
        mock.return_value = True
        yield mock

@pytest.fixture(scope="function")
def mock_datetime():
    """Mock datetime."""
    mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    with patch('datetime.datetime') as mock:
        mock.now.return_value = mock_now
        mock.UTC = UTC
        yield mock

@pytest.fixture(scope="session")
def test_birthdays_config():
    """Fixture providing test birthday configuration."""
    return {
        "04-16": {"name": "Test Person"},
        "04-23": {"name": "Felix"},
        "04-21": {"name": "Pearl"}
    }

@pytest.fixture(scope="session")
def test_weather_data():
    """Fixture providing test weather data."""
    return {
        "temperature": 72,
        "feels_like": 70,
        "description": "sunny",
        "humidity": 50,
        "wind_speed": 5,
        "sunrise": "6:00 AM",
        "sunset": "8:00 PM"
    }

@pytest.fixture(scope="session")
def test_national_days():
    """Fixture providing test national days data."""
    return [
        {
            "name": "National Test Day",
            "url": "https://example.com",
            "occurrence_text": "Annual"
        }
    ] 