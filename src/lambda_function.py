import json
import logging
import requests
from typing import Dict, Any

from config import env, initialize
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

initialize()
logger = logging.getLogger(__name__)


def is_test_mode(event: Dict) -> bool:
    """Check if we're in test mode based on event or environment variable."""
    test_mode = env.test_mode or event.get("test_mode", False)
    if test_mode:
        logger.info({
            "event": "test_mode_enabled",
            "source": "environment" if env.test_mode else "event",
            "message": "Additional logging will be shown"
        })
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
        # Add request ID to logger if available
        if context and hasattr(context, "aws_request_id"):
            logger.aws_request_id = context.aws_request_id

        test_mode = is_test_mode(event)
        test_date = event.get("test_date")

        if test_mode:
            logger.info({
                "event": "test_date_set",
                "test_date": test_date if test_date else "Not specified"
            })

        # Check birthdays
        birthdays = check_birthdays(test_date)
        if test_mode:
            logger.info({
                "event": "birthdays_found",
                "count": len(birthdays) if birthdays else 0
            })

        if birthdays:
            for birthday in birthdays:
                if test_mode:
                    logger.info({
                        "event": "processing_birthday",
                        "name": birthday["name"]
                    })

                # Generate and send birthday messages
                felix_message = generate_felix_birthday_message(birthday)
                pearl_message = generate_pearl_birthday_message(birthday)

                if test_mode:
                    if felix_message:
                        logger.info({"event": "felix_message_generated"})
                    if pearl_message:
                        logger.info({"event": "pearl_message_generated"})

                if felix_message:
                    send_felix_message(felix_message, test_mode)
                if pearl_message:
                    send_pearl_message(pearl_message, test_mode)

                # Generate and send thank you messages
                felix_thank_you = generate_felix_thank_you_message(birthday)
                pearl_thank_you = generate_pearl_thank_you_message(birthday)

                if test_mode:
                    if felix_thank_you:
                        logger.info({"event": "felix_thank_you_generated"})
                    if pearl_thank_you:
                        logger.info({"event": "pearl_thank_you_generated"})

                if felix_thank_you:
                    send_felix_message(felix_thank_you, test_mode)
                if pearl_thank_you:
                    send_pearl_message(pearl_thank_you, test_mode)

        # Get national days
        national_days, error = get_national_days()
        if test_mode:
            if national_days:
                logger.info({
                    "event": "national_days_found",
                    "count": len(national_days)
                })
            elif error:
                logger.error({
                    "event": "national_days_error",
                    "error": error
                })

        if national_days and not error:
            message = generate_national_days_message(national_days)
            if message:
                if test_mode:
                    logger.info({"event": "national_days_message_generated"})
                send_felix_message(message, test_mode)
        elif error:
            logger.error({
                "event": "national_days_error",
                "error": error
            })

        # Get weather
        weather_data = get_weather()
        if test_mode and weather_data:
            logger.info({
                "event": "weather_data_retrieved",
                "location": env.weather_location
            })

        if weather_data:
            message = generate_weather_message(weather_data)
            if message:
                if test_mode:
                    logger.info({"event": "weather_message_generated"})
                send_pearl_message(message, test_mode)

        if test_mode:
            logger.info({"event": "all_tasks_completed"})

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Successfully processed all tasks"}),
        }

    except KeyError as e:
        error_msg = f"Missing required field in event data: {str(e)}"
        logger.error({
            "event": "key_error",
            "error": error_msg,
            "field": str(e)
        })
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_msg}),
        }
    except ValueError as e:
        error_msg = f"Invalid data format: {str(e)}"
        logger.error({
            "event": "value_error",
            "error": error_msg
        })
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_msg}),
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"External API request failed: {str(e)}"
        logger.error({
            "event": "request_error",
            "error": error_msg,
            "type": type(e).__name__
        })
        return {
            "statusCode": 502,
            "body": json.dumps({"error": error_msg}),
        }
    except Exception as e:
        error_msg = f"Unexpected error in lambda_handler: {str(e)}"
        logger.error({
            "event": "unexpected_error",
            "error": error_msg,
            "type": type(e).__name__
        })
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_msg}),
        }
