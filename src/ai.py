import logging
from typing import Dict, List, Optional

import anthropic

from config import FELIX, PEARL, env
from prompts import (
    NATIONAL_DAYS_PROMPT,
    WEATHER_PROMPT,
)
from services.national_days import NationalDay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)


def generate_message_with_claude(prompt: str, character: Dict) -> str:
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
        # Format the detailed weather data for the prompt
        prompt = WEATHER_PROMPT.format(
            full_name=PEARL["full_name"],
            description=PEARL["description"],
            location=env.weather_location,
            temperature=weather_data["temp"],
            feels_like=weather_data["feels_like"],
            weather_description=weather_data["description"],
            humidity=weather_data["humidity"],
            pressure=weather_data["pressure"],
            wind_speed=weather_data["wind_speed"],
            wind_gust_line=(
                f" (gusts up to {weather_data['wind_gust']} mph)"
                if "wind_gust" in weather_data
                else ""
            ),
            clouds=weather_data["clouds"],
            visibility=weather_data["visibility"],
            temp_max=weather_data["temp_max"],
            temp_min=weather_data["temp_min"],
            morning_weather=weather_data["morning_weather"],
            day_weather=weather_data["day_weather"],
            evening_weather=weather_data["evening_weather"],
            night_weather=weather_data["night_weather"],
            pop=weather_data["pop"],  # Precipitation probability
            rain_line=f" Expect rain: {weather_data['rain']} mm" if "rain" in weather_data else "",
            snow_line=f" Expect snow: {weather_data['snow']} mm" if "snow" in weather_data else "",
            sunrise=weather_data["sunrise"],
            sunset=weather_data["sunset"],
        )

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
