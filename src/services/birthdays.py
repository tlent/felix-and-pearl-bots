import logging
from datetime import datetime
from typing import Dict, List, Optional

import anthropic
import pytz
from dotenv import load_dotenv

from src.config.config import BIRTHDAYS, FELIX, PEARL, env
from src.config.prompts import (
    OWN_BIRTHDAY_PROMPT,
    OTHER_BIRTHDAY_PROMPT,
    THANK_YOU_PROMPT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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
    if date_str in BIRTHDAYS:
        birthdays.append(BIRTHDAYS[date_str])
        logger.info(f"Found birthday for {BIRTHDAYS[date_str]['name']}!")

    return birthdays


def generate_message_with_claude(prompt: str, character: Dict) -> str:
    """
    Generate a message using Claude from a character's perspective.
    Args:
        prompt: The prompt to send to Claude
        character: Dictionary containing character information (name, description, etc.)
    """
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {character['full_name']}, {character['description']}.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


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
