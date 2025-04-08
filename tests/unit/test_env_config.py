import os
import pytest
from unittest.mock import patch
import json

def test_required_env_vars_present(app_env):
    """Test that all required environment variables are present."""
    required_vars = [
        'ANTHROPIC_API_KEY',
        'FELIX_DISCORD_WEBHOOK_URL',
        'PEARL_DISCORD_WEBHOOK_URL',
        'WEATHER_API_KEY',
        'WEATHER_LOCATION',
        'BIRTHDAYS_CONFIG'
    ]
    
    for var in required_vars:
        assert var in os.environ, f"Required environment variable {var} is missing"
        assert os.environ[var], f"Environment variable {var} is empty"

def test_birthdays_config_format(app_env):
    """Test that birthdays config is valid JSON."""
    try:
        config = json.loads(os.environ['BIRTHDAYS_CONFIG'])
        assert isinstance(config, dict), "Birthdays config should be a dictionary"
        for date, data in config.items():
            assert isinstance(data, dict), f"Birthday data for {date} should be a dictionary"
            assert 'name' in data, f"Birthday data for {date} should have a name"
            assert 'is_own_birthday' in data, f"Birthday data for {date} should have is_own_birthday flag"
    except json.JSONDecodeError:
        pytest.fail("Birthdays config is not valid JSON")

def test_numeric_env_vars(app_env):
    """Test that numeric environment variables are valid."""
    pass  # Removed since we no longer have numeric env vars

def test_missing_env_vars():
    """Test handling of missing environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError):
            # Try to access any required environment variable
            _ = os.environ['FAILED_MESSAGES_TABLE']

def test_invalid_birthdays_config():
    """Test handling of invalid birthdays config."""
    with patch.dict(os.environ, {'BIRTHDAYS_CONFIG': 'invalid json'}):
        with pytest.raises(json.JSONDecodeError):
            json.loads(os.environ['BIRTHDAYS_CONFIG'])

def test_required_env_vars():
    """Test that all required environment variables are set."""
    required_vars = [
        'ANTHROPIC_API_KEY',
        'FELIX_DISCORD_WEBHOOK_URL',
        'PEARL_DISCORD_WEBHOOK_URL',
        'WEATHER_API_KEY',
        'BIRTHDAYS_CONFIG'
    ]
    
    for var in required_vars:
        assert var in os.environ, f"Required environment variable {var} is missing"
        assert os.environ[var], f"Environment variable {var} is empty" 