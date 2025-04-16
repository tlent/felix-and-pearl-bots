from datetime import datetime
from typing import List, Optional, TypedDict
import logging
import anthropic

from config import env, FELIX, PEARL
from prompts import (
    OWN_BIRTHDAY_PROMPT,
    OTHER_BIRTHDAY_PROMPT,
    THANK_YOU_PROMPT,
)
from ai import generate_message_with_claude, CharacterInfo


logger = logging.getLogger(__name__)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)


class BirthdayInfo(TypedDict):
    """Information about a birthday."""

    name: str
    date: str


def check_birthdays(test_date: Optional[str] = None) -> List[BirthdayInfo]:
    """
    Check if today is anyone's birthday.

    Args:
        test_date: Optional date string in MM-DD format for testing

    Returns:
        List of BirthdayInfo objects for today's birthdays
    """
    try:
        date_str = test_date or datetime.now().strftime("%m-%d")

        if env.test_mode:
            logger.info(f"📅 Checking birthdays for date: {date_str}")

        if date_str in env.birthdays_config:
            if env.test_mode:
                logger.info(f"🎂 Found birthday for {env.birthdays_config[date_str]}")
            return [{"name": env.birthdays_config[date_str], "date": date_str}]
        return []
    except ValueError as e:
        logger.error(f"❌ Invalid date format in check_birthdays: {str(e)}")
        return []
    except KeyError as e:
        logger.error(f"❌ Error accessing birthdays config: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error in check_birthdays: {str(e)}")
        return []


def generate_birthday_message(birthday_info: BirthdayInfo, character: CharacterInfo) -> str:
    """
    Generate a birthday message using Claude.

    Args:
        birthday_info: Information about the birthday
        character: Character information for message generation

    Returns:
        Generated birthday message or empty string if there's an error
    """
    try:
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

        message = generate_message_with_claude(prompt, character)
        if env.test_mode:
            logger.info(f"🎁 Generated birthday message for {name}")
        return message
    except KeyError as e:
        logger.error(f"❌ Missing required field in birthday_info or character: {str(e)}")
        return ""
    except anthropic.APIError as e:
        logger.error(f"❌ Claude API error generating birthday message: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"❌ Unexpected error generating birthday message: {str(e)}")
        return ""


def generate_thank_you_message(birthday_info: BirthdayInfo, character: CharacterInfo) -> str:
    """
    Generate a thank you message for birthday wishes.

    Args:
        birthday_info: Information about the birthday
        character: Character information for message generation

    Returns:
        Generated thank you message or empty string if there's an error
    """
    try:
        prompt = THANK_YOU_PROMPT.format(
            full_name=character["full_name"], description=character["description"]
        )

        message = generate_message_with_claude(prompt, character)
        if env.test_mode:
            logger.info(f"🎁 Generated thank you message for {character['name']}")
        return message
    except KeyError as e:
        logger.error(f"❌ Missing required field in character info: {str(e)}")
        return ""
    except anthropic.APIError as e:
        logger.error(f"❌ Claude API error generating thank you message: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"❌ Unexpected error generating thank you message: {str(e)}")
        return ""


# Wrapper functions for Felix and Pearl
def generate_felix_birthday_message(birthday_info: BirthdayInfo) -> str:
    """Generate a birthday message from Felix's perspective."""
    return generate_birthday_message(birthday_info, FELIX)


def generate_pearl_birthday_message(birthday_info: BirthdayInfo) -> str:
    """Generate a birthday message from Pearl's perspective."""
    return generate_birthday_message(birthday_info, PEARL)


def generate_felix_thank_you_message(birthday_info: BirthdayInfo) -> str:
    """Generate a thank you message from Felix's perspective."""
    return generate_thank_you_message(birthday_info, FELIX)


def generate_pearl_thank_you_message(birthday_info: BirthdayInfo) -> str:
    """Generate a thank you message from Pearl's perspective."""
    return generate_thank_you_message(birthday_info, PEARL)
