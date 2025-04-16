import logging
from datetime import datetime
from typing import Dict, List, Optional

import anthropic
import pytz

from config import FELIX, PEARL, env
from prompts import (
    OWN_BIRTHDAY_PROMPT,
    OTHER_BIRTHDAY_PROMPT,
    THANK_YOU_PROMPT,
)
from ai import generate_message_with_claude

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)


def check_birthdays(test_date: Optional[str] = None) -> List[Dict]:
    """
    Check if today is anyone's birthday.
    Args:
        test_date: Optional date string in MM-DD format for testing
    Returns a list of birthday entries for today.
    """
    if test_date:
        # Use the provided test date
        date_str = test_date
        logger.info(f"Using test date: {date_str}")
    else:
        # Get current date in Eastern Time
        eastern = pytz.timezone("America/New_York")
        now = datetime.now(eastern)
        date_str = now.strftime("%m-%d")

    # Check if today is anyone's birthday
    birthdays = []
    if date_str in env.birthdays_config:
        birthdays.append(env.birthdays_config[date_str])
        logger.info(f"Found birthday for {env.birthdays_config[date_str]}!")

    return birthdays


def generate_birthday_message(birthday_info: Dict, character: Dict) -> str:
    """
    Generate a birthday message using Claude.
    Args:
        birthday_info: Dictionary containing birthday information
        character: Dictionary containing character information
    """
    name = birthday_info["name"]
    is_own_birthday = name == character["name"]

    if is_own_birthday:
        prompt = OWN_BIRTHDAY_PROMPT.format(
            full_name=character["full_name"], description=character["description"]
        )
    else:
        prompt = OTHER_BIRTHDAY_PROMPT.format(
            full_name=character["full_name"],
            description=character["description"],
            name=name,
        )

    return generate_message_with_claude(prompt, character)


def generate_thank_you_message(birthday_info: Dict, character: Dict) -> str:
    """
    Generate a thank you message for birthday wishes.
    Args:
        birthday_info: Dictionary containing birthday information
        character: Dictionary containing character information
    """
    prompt = THANK_YOU_PROMPT.format(
        full_name=character["full_name"], description=character["description"]
    )

    return generate_message_with_claude(prompt, character)


# Wrapper functions for Felix and Pearl
def generate_felix_birthday_message(birthday_info: Dict) -> str:
    """Generate a birthday message from Felix's perspective."""
    return generate_birthday_message(birthday_info, FELIX)


def generate_pearl_birthday_message(birthday_info: Dict) -> str:
    """Generate a birthday message from Pearl's perspective."""
    return generate_birthday_message(birthday_info, PEARL)


def generate_felix_thank_you_message(birthday_info: Dict) -> str:
    """Generate a thank you message from Felix's perspective."""
    return generate_thank_you_message(birthday_info, FELIX)


def generate_pearl_thank_you_message(birthday_info: Dict) -> str:
    """Generate a thank you message from Pearl's perspective."""
    return generate_thank_you_message(birthday_info, PEARL)
