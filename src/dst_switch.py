import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from zoneinfo import ZoneInfo

from config import logger


def get_current_time() -> datetime:
    """Get current time in America/New_York timezone."""
    return datetime.now(ZoneInfo("America/New_York"))


def is_dst_change_day() -> bool:
    """
    Check if today is a DST change day.
    Returns True if today is either:
    - Second Sunday in March (spring forward)
    - First Sunday in November (fall back)
    """
    now = get_current_time()

    # Check for spring forward (second Sunday in March)
    if now.month == 3:
        first_day = datetime(now.year, 3, 1, tzinfo=ZoneInfo("America/New_York"))
        days_until_sunday = (6 - first_day.weekday()) % 7
        second_sunday = first_day + timedelta(days=days_until_sunday + 7)
        return now.date() == second_sunday.date()

    # Check for fall back (first Sunday in November)
    if now.month == 11:
        first_day = datetime(now.year, 11, 1, tzinfo=ZoneInfo("America/New_York"))
        days_until_sunday = (6 - first_day.weekday()) % 7
        first_sunday = first_day + timedelta(days=days_until_sunday)
        return now.date() == first_sunday.date()

    return False


def update_lambda_schedule(is_dst: bool) -> None:
    """
    Update the Lambda function's schedule based on DST status.

    Args:
        is_dst: Whether we're in Daylight Saving Time
    """
    events_client = boto3.client("events")

    # Update the schedule rules
    if is_dst:
        # EDT schedule (7 AM EDT)
        events_client.put_rule(
            Name="DailyScheduleEDT",
            ScheduleExpression="cron(0 11 * * ? *)",
            State="ENABLED",
        )
        events_client.put_rule(
            Name="DailyScheduleEST",
            ScheduleExpression="cron(0 12 * * ? *)",
            State="DISABLED",
        )
    else:
        # EST schedule (7 AM EST)
        events_client.put_rule(
            Name="DailyScheduleEDT",
            ScheduleExpression="cron(0 11 * * ? *)",
            State="DISABLED",
        )
        events_client.put_rule(
            Name="DailyScheduleEST",
            ScheduleExpression="cron(0 12 * * ? *)",
            State="ENABLED",
        )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for DST switch service.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        Dictionary containing status code and response body
    """
    try:
        logger.info("Checking for DST change")
        # Check if today is a DST change day
        if is_dst_change_day():
            # Get current time to determine if we're in DST
            now = get_current_time()
            is_dst = now.dst() != timedelta(0)
            logger.info(f"DST change detected, switching to {'EDT' if is_dst else 'EST'}")

            # Update the schedule
            update_lambda_schedule(is_dst)

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"message": f'Successfully updated schedule for {"EDT" if is_dst else "EST"}'}
                ),
            }

        logger.info("Not a DST change day")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Not a DST change day"}),
        }

    except Exception as e:
        logger.error(f"Error in DST handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
