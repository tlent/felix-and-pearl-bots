import logging
from typing import Optional, TypedDict
import requests
import json
from datetime import datetime
import pytz

from config import env

logger = logging.getLogger(__name__)

# Weather API configuration
WEATHER_API_KEY = env.weather_api_key
WEATHER_API_URL = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={env.weather_lat}&lon={env.weather_lon}"
    f"&appid={WEATHER_API_KEY}&units=imperial"
    f"&exclude=alerts"
)


class WeatherData(TypedDict):
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    pressure: int
    clouds: int
    visibility: int
    wind_gust: float
    temp_max: float
    temp_min: float
    morning_weather: str
    day_weather: str
    evening_weather: str
    night_weather: str
    pop: float
    rain: float
    snow: float
    sunrise: int
    sunset: int


def get_weather() -> Optional[WeatherData]:
    """
    Get current weather data and daily forecast from OpenWeatherMap API.

    Returns:
        WeatherData dictionary if successful, None if there's an error.
        The dictionary contains all weather fields with appropriate default values.
    """
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant current weather data
        current = data.get("current", {})
        daily = data.get("daily", [{}])[0]  # Get the first day's forecast

        # Convert sunrise/sunset timestamps to local time
        ny_tz = pytz.timezone("America/New_York")
        sunrise_utc = datetime.fromtimestamp(daily.get("sunrise", 0), tz=pytz.UTC)
        sunset_utc = datetime.fromtimestamp(daily.get("sunset", 0), tz=pytz.UTC)

        sunrise_local = sunrise_utc.astimezone(ny_tz)
        sunset_local = sunset_utc.astimezone(ny_tz)

        logger.info(f"🌅 Sunrise UTC: {sunrise_utc.strftime('%H:%M %Z')}")
        logger.info(f"🌅 Sunrise Local: {sunrise_local.strftime('%H:%M %Z')}")
        logger.info(f"🌇 Sunset UTC: {sunset_utc.strftime('%H:%M %Z')}")
        logger.info(f"🌇 Sunset Local: {sunset_local.strftime('%H:%M %Z')}")

        weather_data = {
            "temp": current.get("temp", 0.0),
            "feels_like": current.get("feels_like", 0.0),
            "humidity": current.get("humidity", 0),
            "wind_speed": current.get("wind_speed", 0.0),
            "description": current.get("weather", [{}])[0].get("description", ""),
            "pressure": current.get("pressure", 0),
            "clouds": current.get("clouds", 0),
            "visibility": current.get("visibility", 0),
            "wind_gust": current.get("wind_gust", 0.0),
            # Full-day forecast
            "temp_max": daily.get("temp", {}).get("max", 0.0),
            "temp_min": daily.get("temp", {}).get("min", 0.0),
            "morning_weather": daily.get("weather", [{}])[0].get("description", ""),
            "day_weather": daily.get("weather", [{}])[0].get("description", ""),
            "evening_weather": daily.get("weather", [{}])[0].get("description", ""),
            "night_weather": daily.get("weather", [{}])[0].get("description", ""),
            "pop": daily.get("pop", 0.0),  # Probability of precipitation
            "rain": daily.get("rain", 0.0),
            "snow": daily.get("snow", 0.0),
            # Sun times
            "sunrise": int(sunrise_local.timestamp()),
            "sunset": int(sunset_local.timestamp()),
        }

        logger.info("🌤️ Successfully fetched weather data")
        return weather_data

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch weather data: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"❌ Error parsing weather API response: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON response from weather API: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error processing weather data: {str(e)}")
        return None
