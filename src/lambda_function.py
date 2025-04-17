import json
import logging
import os
from typing import Any

import requests

from src.ai import generate_national_days_message, generate_weather_message
from src.config import Config
from src.discord import send_felix_message, send_pearl_message
from src.services.birthdays import (
    check_birthdays,
    generate_felix_birthday_message,
    generate_felix_thank_you_message,
    generate_pearl_birthday_message,
    generate_pearl_thank_you_message,
)
from src.services.national_days import get_national_days
from src.services.weather import get_weather

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_birthdays(config: Config, test_date: str | None = None) -> None:
    """Process and send birthday messages."""
    birthdays = check_birthdays(config, test_date)
    if not birthdays:
        return

    logger.info({"event": "birthday_check", "count": len(birthdays)})

    for birthday in birthdays:
        logger.info({"event": "processing_birthday", "name": birthday["name"]})

        # Process Felix messages
        if felix_message := generate_felix_birthday_message(config, birthday):
            logger.info({"event": "felix_message_generated", "message": felix_message})
            send_felix_message(config, felix_message)

        if felix_thank_you := generate_felix_thank_you_message(config, birthday):
            logger.info({"event": "felix_thank_you_generated", "message": felix_thank_you})
            send_felix_message(config, felix_thank_you)

        # Process Pearl messages
        if pearl_message := generate_pearl_birthday_message(config, birthday):
            logger.info({"event": "pearl_message_generated", "message": pearl_message})
            send_pearl_message(config, pearl_message)

        if pearl_thank_you := generate_pearl_thank_you_message(config, birthday):
            logger.info({"event": "pearl_thank_you_generated", "message": pearl_thank_you})
            send_pearl_message(config, pearl_thank_you)


def process_national_days(config: Config) -> None:
    """Process and send national days messages."""
    national_days, error = get_national_days()

    if error:
        logger.error({"event": "national_days_error", "error": error})
        return

    if not national_days:
        return

    logger.info({"event": "national_days_found", "count": len(national_days)})

    if message := generate_national_days_message(config, national_days):
        logger.info({"event": "national_days_message_generated", "message": message})
        send_felix_message(config, message)


def process_weather(config: Config) -> None:
    """Process and send weather messages."""
    weather_data = get_weather(config)
    if not weather_data:
        return

    logger.info({"event": "weather_data_retrieved", "location": config.weather_location})

    if message := generate_weather_message(config, weather_data):
        logger.info({"event": "weather_message_generated", "message": message})
        send_pearl_message(config, message)


def handle_error(error: Exception) -> tuple[int, str]:
    """Handle different types of errors and return appropriate status code and message."""
    if isinstance(error, KeyError):
        error_msg = f"Missing required field in event data: {error!s}"
        logger.error({"event": "key_error", "error": error_msg, "field": str(error)})
        return 400, error_msg
    elif isinstance(error, ValueError):
        error_msg = f"Invalid data format: {error!s}"
        logger.error({"event": "value_error", "error": error_msg})
        return 400, error_msg
    elif isinstance(error, requests.exceptions.RequestException):
        error_msg = f"External API request failed: {error!s}"
        logger.error({"event": "request_error", "error": error_msg, "type": type(error).__name__})
        return 502, error_msg
    else:
        error_msg = f"Unexpected error in lambda_handler: {error!s}"
        logger.error(
            {"event": "unexpected_error", "error": error_msg, "type": type(error).__name__}
        )
        return 500, error_msg


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Main Lambda handler function.
    Orchestrates the birthday checks, national days, and weather updates.
    """
    try:
        secret_arn = os.environ.get("SECRET_ARN")
        if not secret_arn:
            raise ValueError("SECRET_ARN environment variable is not set")

        config = Config(secret_arn=secret_arn)
        test_date = event.get("test_date")

        if test_date:
            logger.info({"event": "test_date_set", "test_date": test_date})

        # Process all tasks
        process_birthdays(config, test_date)
        process_national_days(config)
        process_weather(config)

        logger.info({"event": "all_tasks_completed"})
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Successfully processed all tasks"}),
        }

    except Exception as e:
        status_code, error_msg = handle_error(e)
        return {
            "statusCode": status_code,
            "body": json.dumps({"error": error_msg}),
        }
