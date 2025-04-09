import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import anthropic
import boto3
import pytz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import configurations
from birthday_config import BIRTHDAYS
from bot_config import BOT_NAMES, FELIX, PEARL
from env_config import env
from prompts import (
    OWN_BIRTHDAY_PROMPT,
    OTHER_BIRTHDAY_PROMPT,
    THANK_YOU_PROMPT,
    NATIONAL_DAYS_PROMPT,
    WEATHER_PROMPT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Initialize AWS clients
def get_aws_clients():
    """Initialize AWS clients"""
    return {"s3": boto3.client("s3"), "ssm": boto3.client("ssm")}


# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)

# Discord webhooks for both bots
FELIX_WEBHOOK_URL = env.felix_webhook_url
PEARL_WEBHOOK_URL = env.pearl_webhook_url

# Weather API configuration for Pearl's service
WEATHER_API_KEY = env.weather_api_key
WEATHER_API_URL = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={env.weather_lat}&lon={env.weather_lon}"
    f"&appid={WEATHER_API_KEY}&units=imperial"
    f"&exclude=minutely,hourly,daily,alerts"
)


class NationalDay:
    """Represents a national day with its name, URL, and optional occurrence text."""

    def __init__(self, name: str, url: str, occurrence_text: Optional[str] = None):
        self.name = name
        self.url = url
        self.occurrence_text = occurrence_text


def is_test_mode(event: Dict) -> bool:
    """Check if we're in test mode based on event or environment variable."""
    test_mode = env.test_mode or event.get("test_mode", False)
    logger.info(f"Test mode: {test_mode}")
    return test_mode


def check_birthdays(test_date: Optional[str] = None) -> List[Dict]:
    """
    Check if today is anyone's birthday.
    Args:
        test_date: Optional date string in MM-DD format for testing
    Returns a list of birthday entries for today.
    """
    if test_date:
        # Use the provided test date
        date_str = test_date
        logger.info(f"Using test date: {date_str}")
    else:
        # Get current date in Eastern Time
        eastern = pytz.timezone("America/New_York")
        now = datetime.now(eastern)
        date_str = now.strftime("%m-%d")

    # Check if today is anyone's birthday
    birthdays = []
    if date_str in BIRTHDAYS:
        birthdays.append(BIRTHDAYS[date_str])
        logger.info(f"Found birthday for {BIRTHDAYS[date_str]['name']}!")

    return birthdays


def generate_message_with_claude(prompt: str, character: Dict) -> str:
    """
    Generate a message using Claude from a character's perspective.
    Args:
        prompt: The prompt to send to Claude
        character: Dictionary containing character information (name, description, etc.)
    """
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {character['full_name']}, {character['description']}.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_birthday_message(birthday_info: Dict, character: Dict) -> str:
    """
    Generate a birthday message using Claude.
    Args:
        birthday_info: Dictionary containing birthday information
        character: Dictionary containing character information
    """
    name = birthday_info["name"]
    is_own_birthday = name == character["name"]

    if is_own_birthday:
        prompt = OWN_BIRTHDAY_PROMPT.format(
            full_name=character["full_name"], description=character["description"]
        )
    else:
        prompt = OTHER_BIRTHDAY_PROMPT.format(
            full_name=character["full_name"], description=character["description"], name=name
        )

    return generate_message_with_claude(prompt, character)


def generate_thank_you_message(birthday_info: Dict, character: Dict) -> str:
    """
    Generate a thank you message for birthday wishes.
    Args:
        birthday_info: Dictionary containing birthday information
        character: Dictionary containing character information
    """
    prompt = THANK_YOU_PROMPT.format(
        full_name=character["full_name"], description=character["description"]
    )

    return generate_message_with_claude(prompt, character)


def send_discord_message(
    content: str, webhook_url: str, character_name: str, test_mode: bool = False
) -> bool:
    """
    Send a message to Discord using the provided webhook URL.
    Returns True if successful, False otherwise.

    Args:
        content: The message content to send
        webhook_url: The Discord webhook URL to use
        character_name: The name of the character sending the message (for logging)
        test_mode: Whether we're in test mode
    """
    try:
        if test_mode:
            logger.info(f"Test mode: Would send {character_name}'s message: {content}")
            return True

        response = requests.post(webhook_url, json={"content": content}, timeout=10)

        if response.status_code == 204:
            logger.info(f"{character_name}'s message sent successfully")
            return True
        else:
            logger.error(f"Failed to send {character_name}'s message: HTTP {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error sending {character_name}'s message: {str(e)}")
        return False


# Wrapper functions for Felix and Pearl
def generate_felix_birthday_message(birthday_info: Dict) -> str:
    """Generate a birthday message from Felix's perspective."""
    return generate_birthday_message(birthday_info, FELIX)


def generate_pearl_birthday_message(birthday_info: Dict) -> str:
    """Generate a birthday message from Pearl's perspective."""
    return generate_birthday_message(birthday_info, PEARL)


def generate_felix_thank_you_message(birthday_info: Dict) -> str:
    """Generate a thank you message from Felix's perspective."""
    return generate_thank_you_message(birthday_info, FELIX)


def generate_pearl_thank_you_message(birthday_info: Dict) -> str:
    """Generate a thank you message from Pearl's perspective."""
    return generate_thank_you_message(birthday_info, PEARL)


def send_felix_message(content: str, test_mode: bool = False) -> bool:
    """Send a message using Felix's webhook."""
    return send_discord_message(content, env.felix_webhook_url, FELIX["name"], test_mode)


def send_pearl_message(content: str, test_mode: bool = False) -> bool:
    """Send a message using Pearl's webhook."""
    return send_discord_message(content, env.pearl_webhook_url, PEARL["name"], test_mode)


def get_national_days() -> Tuple[List[NationalDay], Optional[str]]:
    """
    Scrapes national days from nationaldaycalendar.com.
    Returns a tuple of (list of national days, error message if any).
    """
    try:
        # Get current date in Eastern Time
        eastern = pytz.timezone("America/New_York")
        now = datetime.now(eastern)
        month = now.strftime("%B").lower()
        day = now.day

        # Construct URL
        url = f"https://www.nationaldaycalendar.com/{month}/{month}-{day}"
        logger.info(f"Fetching national days from: {url}")

        # Make request with proper headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            national_days = []

            # Find all national day cards
            cards = soup.select(".m-card--header a")
            logger.info(f"Found {len(cards)} total cards")

            # Words/phrases that indicate a non-national day entry
            excluded_phrases = [
                "birthdays and events",
                "on this day",
                "historical events",
                "celebrity birthdays",
            ]

            for card in cards:
                try:
                    text = card.get_text(strip=True)
                    logger.debug(f"Processing card: {text}")

                    # Skip if this is not a national day
                    text_lower = text.lower()
                    if any(phrase in text_lower for phrase in excluded_phrases):
                        logger.debug(f"Skipping non-national day entry: {text}")
                        continue

                    # Skip if it doesn't start with "NATIONAL" or "INTERNATIONAL"
                    if not (
                        text.upper().startswith("NATIONAL")
                        or text.upper().startswith("INTERNATIONAL")
                    ):
                        logger.debug(f"Skipping non-national/international day: {text}")
                        continue

                    # Parse name and occurrence text
                    name = text
                    occurrence_text = None

                    # Try different separators
                    for separator in [" | ", " - ", "| ", "- "]:
                        if separator in text:
                            name, occurrence_text = text.split(separator, 1)
                            break

                    national_days.append(
                        NationalDay(
                            name=name.strip(),
                            url=card.get("href", "#"),
                            occurrence_text=occurrence_text.strip() if occurrence_text else None,
                        )
                    )
                except (AttributeError, KeyError) as e:
                    logger.warning(f"Error processing card: {str(e)}")
                    continue

            if not national_days:
                logger.warning("No national days found on the page")
                return [], "No national days found on the page"

            logger.info("Found National Days:")
            for day in national_days:
                logger.info(
                    f"- {day.name}" + (f" ({day.occurrence_text})" if day.occurrence_text else "")
                )

            return national_days, None

        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return [], f"Error parsing HTML: {str(e)}"

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return [], f"Failed to fetch data: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [], f"Unexpected error: {str(e)}"


def get_weather() -> Optional[Dict]:
    """Fetch weather data"""
    try:
        logger.info("Fetching weather from OpenWeather API")
        response = requests.get(env.weather_api_url)
        response.raise_for_status()
        weather_data = response.json()

        # Convert sunrise and sunset times to Eastern timezone
        eastern = pytz.timezone("America/New_York")
        sunrise_time = datetime.fromtimestamp(
            weather_data["current"]["sunrise"], tz=pytz.UTC
        ).astimezone(eastern)
        sunset_time = datetime.fromtimestamp(
            weather_data["current"]["sunset"], tz=pytz.UTC
        ).astimezone(eastern)

        # Extract relevant weather information
        weather = {
            "temperature": round(weather_data["current"]["temp"]),
            "feels_like": round(weather_data["current"]["feels_like"]),
            "description": weather_data["current"]["weather"][0]["description"],
            "humidity": weather_data["current"]["humidity"],
            "wind_speed": round(weather_data["current"]["wind_speed"]),
            "sunrise": sunrise_time.strftime("%I:%M %p"),
            "sunset": sunset_time.strftime("%I:%M %p"),
        }

        logger.info("Weather Data:")
        for key, value in weather.items():
            logger.info(f"{key}: {value}")

        return weather
    except (requests.RequestException, KeyError, ValueError, TypeError, AttributeError) as e:
        # These are non-critical errors that shouldn't fail the entire lambda
        logger.error(f"Error fetching weather (non-critical): {str(e)}")
        return None
    except Exception as e:
        # Unexpected errors should be logged but not crash the lambda
        logger.error(f"Unexpected error fetching weather (non-critical): {str(e)}")
        return None


def generate_weather_message(weather_data: Dict) -> Optional[str]:
    """Generate a weather message using Claude from Pearl's perspective."""
    try:
        logger.info("Generating weather message")

        prompt = WEATHER_PROMPT.format(
            full_name=PEARL["full_name"],
            description=PEARL["description"],
            location=env.weather_location,
            temperature=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            weather_description=weather_data["description"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            sunrise=weather_data["sunrise"],
            sunset=weather_data["sunset"],
        )

        return generate_message_with_claude(prompt, PEARL)
    except Exception as e:
        # Weather message generation errors are non-critical
        logger.error(f"Error generating weather message (non-critical): {str(e)}")
        return None


def generate_national_days_message(national_days: List[NationalDay]) -> Optional[str]:
    """Generate a message about national days from Felix's perspective."""
    try:
        # Format the national days data
        days_text = "\n".join(
            [
                f"- {day.name}" + (f" ({day.occurrence_text})" if day.occurrence_text else "")
                for day in national_days
            ]
        )

        logger.info("National Days Found:")
        logger.info(days_text)

        prompt = NATIONAL_DAYS_PROMPT.format(
            full_name=FELIX["full_name"],
            description=FELIX["description"],
            days_text=days_text,
        )

        return generate_message_with_claude(prompt, FELIX)
    except Exception as e:
        # National days message generation errors are non-critical
        logger.error(f"Error generating national days message (non-critical): {str(e)}")
        return None


def lambda_handler(event, context):
    """
    Main Lambda handler for Felix & Pearl Bot.
    Handles national days, weather updates, and birthday messages.
    """
    try:
        # Check if we're in test mode
        test_mode = is_test_mode(event)
        logger.info("Starting Felix & Pearl Bot execution")

        # Check for birthdays
        birthdays = check_birthdays()
        if birthdays:
            logger.info("Processing birthdays")
            for birthday in birthdays:
                # Generate and send Felix's message
                felix_message = generate_felix_birthday_message(birthday)
                if not send_felix_message(felix_message, test_mode=test_mode):
                    logger.error("Failed to send Felix's birthday message")

                # Generate and send Pearl's message
                pearl_message = generate_pearl_birthday_message(birthday)
                if not send_pearl_message(pearl_message, test_mode=test_mode):
                    logger.error("Failed to send Pearl's birthday message")

                # If it's one of the bots' birthdays, send thank you messages
                if birthday["name"] in BOT_NAMES:
                    thank_you_message = generate_felix_thank_you_message(birthday)
                    if not send_felix_message(thank_you_message, test_mode=test_mode):
                        logger.error("Failed to send Felix's thank you message")

                    thank_you_message = generate_pearl_thank_you_message(birthday)
                    if not send_pearl_message(thank_you_message, test_mode=test_mode):
                        logger.error("Failed to send Pearl's thank you message")

        # Get national days
        national_days, error = get_national_days()
        if error:
            logger.error(f"Error getting national days: {error}")
        elif national_days:
            # Generate and send Felix's message
            felix_message = generate_national_days_message(national_days)
            if felix_message and not send_felix_message(felix_message, test_mode=test_mode):
                logger.error("Failed to send Felix's national days message")

        # Get weather
        weather_data = get_weather()
        if weather_data:
            # Generate and send Pearl's message
            pearl_message = generate_weather_message(weather_data)
            if pearl_message and not send_pearl_message(pearl_message, test_mode=test_mode):
                logger.error("Failed to send Pearl's weather message")

        return {"statusCode": 200, "body": json.dumps("Felix & Pearl Bot execution completed")}

    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
