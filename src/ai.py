import logging
from typing import Dict, List, Optional, TypedDict
import pytz
from datetime import datetime

import anthropic

from config import FELIX, PEARL, env
from prompts import (
    NATIONAL_DAYS_PROMPT,
    WEATHER_PROMPT,
)
from services.national_days import NationalDay

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)


class CharacterInfo(TypedDict):
    name: str
    full_name: str
    description: str


def generate_message_with_claude(prompt: str, character: CharacterInfo) -> str:
    """
    Generate a message using Claude from a character's perspective.
    Args:
        prompt: The prompt to send to Claude
        character: Dictionary containing character information
    """
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {character['full_name']}, {character['description']}.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_weather_message(weather_data: Dict) -> Optional[str]:
    """
    Generate a weather message using Claude with detailed weather data.
    Args:
        weather_data: Dictionary containing detailed weather information
    Returns:
        The generated weather message or None if there's an error.
    """
    try:
        # Format sunrise/sunset times
        ny_tz = pytz.timezone("America/New_York")
        sunrise_dt = datetime.fromtimestamp(weather_data["sunrise"], tz=pytz.UTC).astimezone(ny_tz)
        sunset_dt = datetime.fromtimestamp(weather_data["sunset"], tz=pytz.UTC).astimezone(ny_tz)

        # Format the detailed weather data for the prompt
        formatted_data = {
            "full_name": PEARL["full_name"],
            "description": PEARL["description"],
            "location": env.weather_location,
            "temperature": f"{weather_data['temp']}°F",
            "feels_like": f"{weather_data['feels_like']}°F",
            "weather_description": weather_data["description"],
            "humidity": f"{weather_data['humidity']}%",
            "pressure": f"{weather_data['pressure']} hPa",
            "wind_speed": f"{weather_data['wind_speed']} mph",
            "wind_gust_line": (
                f" (gusts up to {weather_data['wind_gust']} mph)"
                if "wind_gust" in weather_data
                else ""
            ),
            "clouds": f"{weather_data['clouds']}%",
            "visibility": f"{weather_data['visibility']} m",
            "temp_max": f"{weather_data['temp_max']}°F",
            "temp_min": f"{weather_data['temp_min']}°F",
            "morning_weather": weather_data["morning_weather"],
            "day_weather": weather_data["day_weather"],
            "evening_weather": weather_data["evening_weather"],
            "night_weather": weather_data["night_weather"],
            "pop": f"{weather_data['pop'] * 100}%",  # Convert to percentage
            "rain_line": (
                f" Expect rain: {weather_data['rain']} mm"
                if "rain" in weather_data
                else ""
            ),
            "snow_line": (
                f" Expect snow: {weather_data['snow']} mm"
                if "snow" in weather_data
                else ""
            ),
            "sunrise": sunrise_dt.strftime("%I:%M %p"),
            "sunset": sunset_dt.strftime("%I:%M %p"),
        }

        if env.test_mode:
            logger.info("🌤️ Weather data being sent to AI:")
            for key, value in formatted_data.items():
                logger.info(f"  {key}: {value}")

        prompt = WEATHER_PROMPT.format(**formatted_data)
        return generate_message_with_claude(prompt, PEARL)

    except Exception as e:
        logger.error(f"Error generating weather message: {str(e)}")
        return None


def generate_national_days_message(national_days: List[NationalDay]) -> Optional[str]:
    """
    Generate a national days message using Claude.
    Args:
        national_days: List of NationalDay objects
    Returns:
        The generated national days message or None if there's an error.
    """
    try:
        # Format national days for the prompt
        days_text = "\n".join([f"- {day.name}" for day in national_days])
        prompt = NATIONAL_DAYS_PROMPT.format(
            full_name=FELIX["full_name"], description=FELIX["description"], days_text=days_text
        )

        return generate_message_with_claude(prompt, FELIX)

    except Exception as e:
        logger.error(f"Error generating national days message: {str(e)}")
        return None
