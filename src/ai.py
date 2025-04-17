import logging

from anthropic.types import TextBlock

from src.config import Config
from src.prompts import (
    FELIX,
    NATIONAL_DAYS_PROMPT,
    PEARL,
    WEATHER_PROMPT,
    CharacterInfo,
    get_system_prompt,
)
from src.services.national_days import NationalDay
from src.services.weather import (
    PRECIPITATION_CHANCE_THRESHOLD,
    DailyForecast,
    WeatherData,
)

logger = logging.getLogger(__name__)


def generate_message_with_claude(config: Config, prompt: str, character: CharacterInfo) -> str:
    """
    Generate a message using Claude from a character's perspective.
    Args:
        config: Config object
        prompt: The prompt to send to Claude
        character: Dictionary containing character information
    Returns:
        The generated message or None if there's an error.
    """
    response = config.claude_client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.75,
        system=get_system_prompt(character),
        messages=[{"role": "user", "content": prompt}],
    )
    if isinstance(response.content[0], TextBlock):
        return response.content[0].text
    else:
        logger.error(f"Unexpected response content: {response.content[0]}")
        return str(response.content[0])


def format_upcoming_forecast(upcoming: list[DailyForecast]) -> str:
    """Format the upcoming forecast days into a readable string."""
    forecast_lines = []
    for day in upcoming:
        precipitation_info = []
        if day["pop"] > PRECIPITATION_CHANCE_THRESHOLD:
            if day["rain"] > 0:
                precipitation_info.append(f"{day['pop']:.0%} chance of rain")
            if day["snow"] > 0:
                precipitation_info.append(f"{day['pop']:.0%} chance of snow")

        forecast_lines.append(
            f"- {day['date']:%A}: High {day['high']}°F, Low {day['low']}°F"
            f" - {day['description'].upper()}"
            f"{f' ({", ".join(precipitation_info)})' if precipitation_info else ''}"
        )
    return "\n".join(forecast_lines)


def generate_weather_message(config: Config, weather_data: WeatherData) -> str | None:
    """Generate a weather message using Claude with the provided weather data."""
    try:
        # Format the upcoming forecast section
        upcoming_forecast = format_upcoming_forecast(weather_data["upcoming"])

        # Format rain and snow information for today
        rain_info = (
            f", {weather_data['today']['rain']}mm rain expected"
            if weather_data["today"]["rain"] > 0
            else ""
        )
        snow_info = (
            f", {weather_data['today']['snow']}mm snow expected"
            if weather_data["today"]["snow"] > 0
            else ""
        )

        prompt = WEATHER_PROMPT.format(
            full_name=PEARL["full_name"],
            description=PEARL["description"],
            location=config.weather_location,
            current=weather_data["current"],
            today=weather_data["today"],
            upcoming_forecast=upcoming_forecast,
            sunrise=weather_data["sunrise"],
            sunset=weather_data["sunset"],
            moon_phase=weather_data["moon_phase"],
            rain_info=rain_info,
            snow_info=snow_info,
        )
        return generate_message_with_claude(config, prompt, PEARL)
    except Exception as e:
        logger.error(f"Error generating weather message: {e!s}")
        return None


def generate_national_days_message(config: Config, national_days: list[NationalDay]) -> str | None:
    """
    Generate a national days message using Claude.
    Args:
        config: Config object
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

        return generate_message_with_claude(config, prompt, FELIX)

    except Exception as e:
        logger.error(f"Error generating national days message: {e!s}")
        return None
