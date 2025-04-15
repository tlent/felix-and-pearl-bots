import logging
from typing import Dict, List, Optional

import anthropic
from dotenv import load_dotenv

from src.config.config import FELIX, PEARL, env
from src.config.prompts import (
    NATIONAL_DAYS_PROMPT,
    WEATHER_PROMPT,
)
from src.services.national_days import NationalDay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=env.anthropic_api_key)


def generate_weather_message(weather_data: Dict) -> Optional[str]:
    """
    Generate a weather message using Claude.
    Args:
        weather_data: Dictionary containing weather information
    Returns the generated message or None if there's an error.
    """
    try:
        prompt = WEATHER_PROMPT.format(
            temp=weather_data["temp"],
            feels_like=weather_data["feels_like"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            description=weather_data["description"],
        )

        response = claude.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1000,
            temperature=0.7,
            system=f"You are {PEARL['full_name']}, {PEARL['description']}.",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    except Exception as e:
        logger.error(f"Error generating weather message: {str(e)}")
        return None


def generate_national_days_message(national_days: List[NationalDay]) -> Optional[str]:
    """
    Generate a national days message using Claude.
    Args:
        national_days: List of NationalDay objects
    Returns the generated message or None if there's an error.
    """
    try:
        # Format national days for the prompt
        days_text = "\n".join([f"- {day.name}" for day in national_days])
        prompt = NATIONAL_DAYS_PROMPT.format(days=days_text)

        response = claude.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1000,
            temperature=0.7,
            system=f"You are {FELIX['full_name']}, {FELIX['description']}.",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    except Exception as e:
        logger.error(f"Error generating national days message: {str(e)}")
        return None
