import os
import json
from unittest.mock import patch
from birthday_config import load_birthdays, BIRTHDAYS, MESSAGE_TYPES

def test_load_birthdays_valid_json():
    """Test loading birthdays with valid JSON configuration."""
    test_config = {
        "04-16": {"name": "Test Person"}
    }
    with patch.dict(os.environ, {'BIRTHDAYS_CONFIG': json.dumps(test_config)}):
        result = load_birthdays()
        assert result == test_config

def test_load_birthdays_invalid_json():
    """Test loading birthdays with invalid JSON configuration."""
    with patch.dict(os.environ, {'BIRTHDAYS_CONFIG': 'invalid json'}):
        result = load_birthdays()
        assert result == {}

def test_load_birthdays_missing_env():
    """Test loading birthdays when environment variable is not set."""
    with patch.dict(os.environ, {}, clear=True):
        result = load_birthdays()
        assert result == {}

def test_message_types():
    """Test that message types are correctly defined."""
    assert MESSAGE_TYPES == {
        "friend": "friend_birthday",
        "self": "self_birthday"
    } 