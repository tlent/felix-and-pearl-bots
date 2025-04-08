import os
import pytest
from unittest.mock import patch, MagicMock
from lambda_function import (
    generate_birthday_message,
    generate_thank_you_message,
    generate_weather_message,
    generate_message,
    NationalDay,
    generate_felix_birthday_message,
    generate_pearl_birthday_message
)

@pytest.fixture
def mock_env():
    """Fixture to set up test environment variables."""
    test_env = {
        'ANTHROPIC_API_KEY': 'test_key',
        'FELIX_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'PEARL_DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test',
        'WEATHER_API_KEY': 'test_weather_key',
        'WEATHER_LOCATION': 'Test City,TS,US',
        'BIRTHDAYS_CONFIG': '{"04-16": {"name": "Test Person", "is_own_birthday": false}}'
    }
    with patch.dict(os.environ, test_env):
        yield test_env

@pytest.fixture
def mock_claude():
    """Fixture to mock Claude API responses."""
    with patch('lambda_function.claude') as mock:
        mock.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Test message")]
        )
        yield mock

def test_generate_birthday_message(mock_env, mock_claude):
    """Test generating a birthday message."""
    # Test data
    birthday_info = {
        'name': 'Test Person',
        'is_own_birthday': False
    }
    
    # Mock Claude response
    mock_claude.messages.create.return_value.content = [type('obj', (object,), {'text': 'Happy Birthday Test Person!'})]
    
    # Test Felix's message
    message = generate_felix_birthday_message(birthday_info)
    assert message == 'Happy Birthday Test Person!'
    
    # Test Pearl's message
    message = generate_pearl_birthday_message(birthday_info)
    assert message == 'Happy Birthday Test Person!'

def test_generate_thank_you_message(mock_env, mock_claude):
    """Test generating a thank you message."""
    birthday_info = {
        "name": "Felix",
        "is_own_birthday": True
    }
    message = generate_thank_you_message(birthday_info, is_felix=True)
    assert message == "Test message"
    mock_claude.messages.create.assert_called_once()

def test_generate_weather_message(mock_env, mock_claude):
    """Test generating a weather message."""
    weather_data = {
        "temperature": 72,
        "feels_like": 70,
        "description": "sunny",
        "humidity": 50,
        "wind_speed": 5,
        "sunrise": "6:00 AM",
        "sunset": "8:00 PM"
    }
    message = generate_weather_message(weather_data)
    assert message == "Test message"
    mock_claude.messages.create.assert_called_once()

def test_generate_message_national_days(mock_env, mock_claude):
    """Test generating a message about national days."""
    national_days = [
        NationalDay(
            name="National Test Day",
            url="https://example.com",
            occurrence_text="Annual"
        )
    ]
    message = generate_message(national_days)
    assert message == "Test message"
    mock_claude.messages.create.assert_called_once() 