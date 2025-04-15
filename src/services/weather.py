import logging
from typing import Optional, Dict

import requests
from dotenv import load_dotenv

from src.config.config import env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Weather API configuration
WEATHER_API_KEY = env.weather_api_key
WEATHER_API_URL = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={env.weather_lat}&lon={env.weather_lon}"
    f"&appid={WEATHER_API_KEY}&units=imperial"
    f"&exclude=minutely,hourly,daily,alerts"
)


def get_weather() -> Optional[Dict]:
    """
    Get current weather data from OpenWeatherMap API.
    Returns weather data dictionary or None if there's an error.
    """
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant weather data
        current = data.get("current", {})
        weather_data = {
            "temp": current.get("temp"),
            "feels_like": current.get("feels_like"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_speed"),
            "description": current.get("weather", [{}])[0].get("description", ""),
        }

        logger.info("Successfully fetched weather data")
        return weather_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing weather data: {str(e)}")
        return None
