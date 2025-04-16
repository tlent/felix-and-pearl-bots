import sys
import os
import logging
import json


def initialize():
    setup_logging()


def setup_logging():
    """Configure logging for the entire application with AWS Lambda specific formatting."""

    # Create a formatter that includes Lambda request ID when available
    class LambdaFormatter(logging.Formatter):
        def format(self, record):
            # Add Lambda request ID if available
            if hasattr(record, "aws_request_id"):
                record.msg = f"[{record.aws_request_id}] {record.msg}"

            # Handle structured logging
            if isinstance(record.msg, dict):
                record.msg = json.dumps(record.msg)

            return super().format(record)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        LambdaFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(console_handler)


# Initialize logging
setup_logging()

# Bot names and identities
FELIX = {
    "name": "Felix",
    "full_name": "Sir Felix Whiskersworth",
    "description": "a distinguished feline who loves to share interesting facts",
    "birthday": "07-16",
}

PEARL = {
    "name": "Pearl",
    "full_name": "Lady Pearl Weatherpaws",
    "description": "a sophisticated cat who loves weather and is witty and playful",
    "birthday": "04-23",
}


def get_env_var(name: str) -> str:
    """Get environment variable. Raises ValueError if not found.

    Args:
        name: Name of the environment variable

    Returns:
        Value of the environment variable

    Raises:
        ValueError: If environment variable is not found
    """
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Required environment variable {name} not found")
    return value


def parse_birthdays_config(birthdays_str: str) -> dict:
    """Parse birthdays configuration string into a dictionary.

    Args:
        birthdays_str: String in format "MM-DD:Name,MM-DD:Name"

    Returns:
        Dictionary mapping dates (MM-DD) to names

    Raises:
        ValueError: If the string format is invalid
    """
    if not birthdays_str:
        return {}

    birthdays_config = {}
    try:
        for entry in birthdays_str.split(","):
            entry = entry.strip()
            if not entry:
                continue

            if ":" not in entry:
                raise ValueError(f"Invalid birthday format: '{entry}'. Expected 'MM-DD:Name'")

            date, name = entry.split(":", 1)
            date = date.strip()
            name = name.strip()

            if not date or not name:
                raise ValueError(f"Empty date or name in entry: '{entry}'")

            # Validate date format (MM-DD)
            try:
                month, day = date.split("-")
                if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                    raise ValueError(
                        f"Invalid date in entry: '{entry}'. " "Month must be 1-12, day must be 1-31"
                    )
            except ValueError as e:
                raise ValueError(f"Invalid date format in entry: '{entry}'. Expected MM-DD") from e

            birthdays_config[date] = name

    except Exception as e:
        raise ValueError(
            f"Error parsing BIRTHDAYS_CONFIG: {str(e)}. " "Format should be 'MM-DD:Name,MM-DD:Name'"
        ) from e

    return birthdays_config


class EnvConfig:
    def __init__(self):
        self.test_mode = get_env_var("TEST_MODE")
        self.felix_webhook_url = get_env_var("FELIX_DISCORD_WEBHOOK_URL")
        self.pearl_webhook_url = get_env_var("PEARL_DISCORD_WEBHOOK_URL")
        self.anthropic_api_key = get_env_var("ANTHROPIC_API_KEY")
        self.weather_api_key = get_env_var("WEATHER_API_KEY")
        self.weather_location = get_env_var("WEATHER_LOCATION")
        self.weather_lat = get_env_var("WEATHER_LAT")
        self.weather_lon = get_env_var("WEATHER_LON")

        # Parse birthdays from simple format: "MM-DD:Name,MM-DD:Name"
        birthdays_str = get_env_var("BIRTHDAYS_CONFIG")
        self.birthdays_config = parse_birthdays_config(birthdays_str)


env = EnvConfig()
