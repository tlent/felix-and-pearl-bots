import logging
from datetime import datetime
from typing import TypedDict

import anthropic

from src.ai import CharacterInfo, generate_message_with_claude
from src.config import Config
from src.prompts import (
    FELIX,
    OTHER_BIRTHDAY_PROMPT,
    OWN_BIRTHDAY_PROMPT,
    PEARL,
    THANK_YOU_PROMPT,
)

logger = logging.getLogger(__name__)


class BirthdayInfo(TypedDict):
    """Information about a birthday."""

    name: str
    date: str


def check_birthdays(config: Config, test_date: str | None = None) -> list[BirthdayInfo]:
    """
    Check if today is anyone's birthday.

    Args:
        test_date: Optional date string in MM-DD format for testing

    Returns:
        List of BirthdayInfo objects for today's birthdays
    """
    try:
        date_str = test_date or datetime.now().strftime("%m%d")

        logger.info(f"📅 Checking birthdays for date: {date_str}")

        if date_str in config.birthdays_config:
            logger.info(f"🎂 Found birthday for {config.birthdays_config[date_str]}")
            return [{"name": config.birthdays_config[date_str], "date": date_str}]
        return []
    except ValueError as e:
        logger.error(f"❌ Invalid date format in check_birthdays: {e!s}")
        return []
    except KeyError as e:
        logger.error(f"❌ Error accessing birthdays config: {e!s}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error in check_birthdays: {e!s}")
        return []


def generate_birthday_message(
    config: Config, birthday_info: BirthdayInfo, character: CharacterInfo
) -> str:
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

        message = generate_message_with_claude(config, prompt, character)
        logger.info(f"🎁 Generated birthday message for {name}")
        return message
    except KeyError as e:
        logger.error(f"❌ Missing required field in birthday_info or character: {e!s}")
        return ""
    except anthropic.APIError as e:
        logger.error(f"❌ Claude API error generating birthday message: {e!s}")
        return ""
    except Exception as e:
        logger.error(f"❌ Unexpected error generating birthday message: {e!s}")
        return ""


def generate_thank_you_message(
    config: Config, birthday_info: BirthdayInfo, character: CharacterInfo
) -> str:
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

        message = generate_message_with_claude(config, prompt, character)
        logger.info(f"🎁 Generated thank you message for {character['name']}")
        return message
    except KeyError as e:
        logger.error(f"❌ Missing required field in character info: {e!s}")
        return ""
    except anthropic.APIError as e:
        logger.error(f"❌ Claude API error generating thank you message: {e!s}")
        return ""
    except Exception as e:
        logger.error(f"❌ Unexpected error generating thank you message: {e!s}")
        return ""


# Wrapper functions for Felix and Pearl
def generate_felix_birthday_message(config: Config, birthday_info: BirthdayInfo) -> str:
    """Generate a birthday message from Felix's perspective."""
    return generate_birthday_message(config, birthday_info, FELIX)


def generate_pearl_birthday_message(config: Config, birthday_info: BirthdayInfo) -> str:
    """Generate a birthday message from Pearl's perspective."""
    return generate_birthday_message(config, birthday_info, PEARL)


def generate_felix_thank_you_message(config: Config, birthday_info: BirthdayInfo) -> str:
    """Generate a thank you message from Felix's perspective."""
    return generate_thank_you_message(config, birthday_info, FELIX)


def generate_pearl_thank_you_message(config: Config, birthday_info: BirthdayInfo) -> str:
    """Generate a thank you message from Pearl's perspective."""
    return generate_thank_you_message(config, birthday_info, PEARL)
