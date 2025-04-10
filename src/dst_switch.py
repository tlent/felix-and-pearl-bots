import boto3
import datetime
import pytz


def lambda_handler(event, context):
    """
    Lambda function to switch between EDT and EST schedules based on DST.
    Runs on the second Sunday in March and first Sunday in November.
    """
    events = boto3.client("events")
    ny_tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(ny_tz)

    # Get current month and day
    current_month = now.month
    current_day = now.day

    # Check if we're in DST
    is_dst = now.dst() != datetime.timedelta(0)

    if current_month == 3 and 8 <= current_day <= 14:  # Second Sunday in March
        # Enable EDT schedule (7 AM EDT = 11:00 UTC)
        events.put_rule(
            Name="DailyScheduleEDT",
            ScheduleExpression="cron(0 11 * * ? *)",
            State="ENABLED",
        )
        # Disable EST schedule
        events.put_rule(Name="DailyScheduleEST", State="DISABLED")
        return {
            "statusCode": 200,
            "body": "Successfully switched to EDT schedule (7 AM EDT)",
        }
    elif current_month == 11 and 1 <= current_day <= 7:  # First Sunday in November
        # Enable EST schedule (7 AM EST = 12:00 UTC)
        events.put_rule(
            Name="DailyScheduleEST",
            ScheduleExpression="cron(0 12 * * ? *)",
            State="ENABLED",
        )
        # Disable EDT schedule
        events.put_rule(Name="DailyScheduleEDT", State="DISABLED")
        return {
            "statusCode": 200,
            "body": "Successfully switched to EST schedule (7 AM EST)",
        }

    # If we're not on a DST transition day, just return success
    return {
        "statusCode": 200,
        "body": f'No schedule change needed. Currently in {"EDT" if is_dst else "EST"}',
    }
