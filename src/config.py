import boto3
from botocore.exceptions import ClientError
import json
import anthropic
import os

from src.prompts import FELIX, PEARL


class Config:
    def __init__(self, secret_arn: str):
        secrets = load_secrets(secret_arn)
        self.felix_webhook_url = secrets["FELIX_DISCORD_WEBHOOK_URL"]
        self.pearl_webhook_url = secrets["PEARL_DISCORD_WEBHOOK_URL"]
        self.weather_api_key = secrets["WEATHER_API_KEY"]
        self.weather_location = secrets["WEATHER_LOCATION"]
        self.weather_lat = secrets["WEATHER_LAT"]
        self.weather_lon = secrets["WEATHER_LON"]

        birthdays_str = secrets["BIRTHDAYS_CONFIG"]
        self.birthdays_config = parse_birthdays_config(birthdays_str)

        self.claude_client = anthropic.Anthropic(api_key=secrets["ANTHROPIC_API_KEY"])


def load_secrets(secret_arn: str) -> dict:
    # First try to load from local secrets.json for development
    if os.path.exists("secrets.json"):
        try:
            with open("secrets.json", "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load local secrets.json: {e}")
            print("Falling back to AWS Secrets Manager...")

    # If local secrets.json doesn't exist or fails, try AWS Secrets Manager
    client = boto3.client("secretsmanager")

    try:
        response = client.get_secret_value(SecretId=secret_arn)
        secret = response["SecretString"]
        secret_dict = json.loads(secret)

        return secret_dict

    except ClientError as e:
        raise ValueError(f"Unable to retrieve secret: {e}")
    except json.JSONDecodeError:
        raise ValueError("Failed to decode the secret string as JSON")


def parse_birthdays_config(birthdays_str: str) -> dict:
    """Parse birthdays configuration string into a dictionary."""
    birthdays_config = {
        FELIX["name"]: FELIX["birthday"],
        PEARL["name"]: PEARL["birthday"],
    }

    for entry in birthdays_str.split(","):
        entry = entry.strip()
        if not entry:
            continue

        if ":" not in entry:
            raise ValueError(f"Invalid format: '{entry}', expected 'MMDD:Name'")

        date, name = entry.split(":", 1)
        date = date.strip()
        name = name.strip()

        # Validate MMDD format for date
        if not (len(date) == 4 and date.isdigit()):
            raise ValueError(f"Invalid date: '{date}', must be MMDD")
        month, day = date[:2], date[2:]
        if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
            raise ValueError(f"Invalid date: '{date}', month 1-12 and day 1-31 expected")

        birthdays_config[date] = name

    return birthdays_config
