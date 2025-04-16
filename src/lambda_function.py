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

        test_date = event.get("test_date")

        if test_date:
            logger.info({
                "event": "test_date_set",
                "test_date": test_date
            })

        # Check birthdays
        birthdays = check_birthdays(test_date)
        logger.info({
            "event": "birthday_check",
            "count": len(birthdays) if birthdays else 0
        })

        if birthdays:
            for birthday in birthdays:
                logger.info({
                    "event": "processing_birthday",
                    "name": birthday["name"]
                })

                # Generate and send birthday messages
                felix_message = generate_felix_birthday_message(birthday)
                if felix_message:
                    logger.info({"event": "felix_message_generated"})

                pearl_message = generate_pearl_birthday_message(birthday)
                if pearl_message:
                    logger.info({"event": "pearl_message_generated"})

                if felix_message:
                    send_felix_message(felix_message)
                if pearl_message:
                    send_pearl_message(pearl_message)

                # Generate and send thank you messages
                felix_thank_you = generate_felix_thank_you_message(birthday)
                if felix_thank_you:
                    logger.info({"event": "felix_thank_you_generated"})
                pearl_thank_you = generate_pearl_thank_you_message(birthday)
                if pearl_thank_you:
                    logger.info({"event": "pearl_thank_you_generated"})

                if felix_thank_you:
                    send_felix_message(felix_thank_you)
                if pearl_thank_you:
                    send_pearl_message(pearl_thank_you)

        # Get national days
        national_days, error = get_national_days()
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
                logger.info({"event": "national_days_message_generated"})
                send_felix_message(message)
        elif error:
            logger.error({
                "event": "national_days_error",
                "error": error
            })

        # Get weather
        weather_data = get_weather()
        if weather_data:
            logger.info({
                "event": "weather_data_retrieved",
                "location": env.weather_location
            })

        if weather_data:
            message = generate_weather_message(weather_data)
            if message:
                logger.info({"event": "weather_message_generated"})
                send_pearl_message(message)

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
