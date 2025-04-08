"""
Birthday configuration for Felix & Pearl Bot.
This file contains birthday information in a format that doesn't expose personal details.
"""

import os
import json
from typing import Dict

def load_birthdays() -> Dict:
    """Load birthday configuration from environment variable."""
    birthdays_json = os.environ.get('BIRTHDAYS_CONFIG', '{}')
    try:
        return json.loads(birthdays_json)
    except json.JSONDecodeError:
        return {}

# Birthday configuration loaded from environment variable
# Format: {"MM-DD": {"name": "display_name", "is_own_birthday": boolean}}
BIRTHDAYS = load_birthdays()

# Message types for birthday messages
MESSAGE_TYPES = {
    "friend": "friend_birthday",
    "self": "self_birthday"
} 