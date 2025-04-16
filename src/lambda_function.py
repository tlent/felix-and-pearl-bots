import json
import logging
from typing import Dict, Any

from config import env
from ai import generate_national_days_message, generate_weather_message
from discord import send_felix_message, send_pearl_message
from services.birthdays import (
    check_birthdays,
    generate_felix_birthday_message,
    generate_pearl_birthday_message,
    generate_felix_thank_you_message,
    generate_pearl_thank_you_message,
)
from services.national_days import get_national_days
from services.weather import get_weather

logger = logging.getLogger(__name__)


def is_test_mode(event: Dict) -> bool:
    """Check if we're in test mode based on event or environment variable."""
    test_mode = env.test_mode or event.get("test_mode", False)
    if test_mode:
        logger.info("🔍 TEST MODE ENABLED - Additional logging will be shown")
    return test_mode


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.
    Orchestrates the birthday checks, national days, and weather updates.

    Args:
        event: Dictionary containing the Lambda event data
        context: Lambda context object
    Returns:
        Dictionary containing the response with status code and body
    """
    try:
        test_mode = is_test_mode(event)
        test_date = event.get("test_date")

        if test_mode:
            logger.info(f"📅 Test date: {test_date if test_date else 'Not specified'}")

        # Check birthdays
        birthdays = check_birthdays(test_date)
        if test_mode:
            logger.info(f"🎂 Found {len(birthdays) if birthdays else 0} birthdays to process")

        if birthdays:
            for birthday in birthdays:
                if test_mode:
                    logger.info(f"🎁 Processing birthday for: {birthday['name']}")

                # Generate and send birthday messages
                felix_message = generate_felix_birthday_message(birthday)
                pearl_message = generate_pearl_birthday_message(birthday)

                if test_mode:
                    if felix_message:
                        logger.info("🐱 Felix birthday message generated")
                    if pearl_message:
                        logger.info("🐱 Pearl birthday message generated")

                if felix_message:
                    send_felix_message(felix_message, test_mode)
                if pearl_message:
                    send_pearl_message(pearl_message, test_mode)

                # Generate and send thank you messages
                felix_thank_you = generate_felix_thank_you_message(birthday)
                pearl_thank_you = generate_pearl_thank_you_message(birthday)

                if test_mode:
                    if felix_thank_you:
                        logger.info("🐱 Felix thank you message generated")
                    if pearl_thank_you:
                        logger.info("🐱 Pearl thank you message generated")

                if felix_thank_you:
                    send_felix_message(felix_thank_you, test_mode)
                if pearl_thank_you:
                    send_pearl_message(pearl_thank_you, test_mode)

        # Get national days
        national_days, error = get_national_days()
        if test_mode:
            if national_days:
                logger.info(f"📅 Found {len(national_days)} national days")
            elif error:
                logger.error(f"❌ Error getting national days: {error}")

        if national_days and not error:
            message = generate_national_days_message(national_days)
            if message:
                if test_mode:
                    logger.info("🐱 National days message generated")
                send_felix_message(message, test_mode)
        elif error:
            logger.error(f"Error getting national days: {error}")

        # Get weather
        weather_data = get_weather()
        if test_mode and weather_data:
            logger.info("🌤️ Weather data retrieved successfully")

        if weather_data:
            message = generate_weather_message(weather_data)
            if message:
                if test_mode:
                    logger.info("🐱 Weather message generated")
                send_pearl_message(message, test_mode)

        if test_mode:
            logger.info("✅ All tasks completed successfully")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Successfully processed all tasks"}),
        }

    except Exception as e:
        logger.error(f"❌ Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
