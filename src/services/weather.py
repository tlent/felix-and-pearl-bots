import requests
from typing import Dict, Optional

from config import logger, env


# Weather API configuration
WEATHER_API_KEY = env.weather_api_key
WEATHER_API_URL = (
    f"https://api.openweathermap.org/data/3.0/onecall"
    f"?lat={env.weather_lat}&lon={env.weather_lon}"
    f"&appid={WEATHER_API_KEY}&units=imperial"
    f"&exclude=alerts"
)


def get_weather() -> Optional[Dict]:
    """
    Get current weather data and daily forecast from OpenWeatherMap API.
    Returns weather data dictionary or None if there's an error.
    """
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant current weather data
        current = data.get("current", {})
        daily = data.get("daily", [{}])[0]  # Get the first day's forecast

        weather_data = {
            "temp": current.get("temp"),
            "feels_like": current.get("feels_like"),
            "humidity": current.get("humidity"),
            "wind_speed": current.get("wind_speed"),
            "description": current.get("weather", [{}])[0].get("description", ""),
            "pressure": current.get("pressure"),
            "clouds": current.get("clouds"),
            "visibility": current.get("visibility"),
            "wind_gust": current.get("wind_gust", 0),
            # Full-day forecast
            "temp_max": daily.get("temp", {}).get("max"),
            "temp_min": daily.get("temp", {}).get("min"),
            "morning_weather": daily.get("weather", [{}])[0].get("description", ""),
            "day_weather": daily.get("weather", [{}])[0].get("description", ""),
            "evening_weather": daily.get("weather", [{}])[0].get("description", ""),
            "night_weather": daily.get("weather", [{}])[0].get("description", ""),
            "pop": daily.get("pop"),  # Probability of precipitation
            "rain": daily.get("rain", 0),
            "snow": daily.get("snow", 0),
            # Sun times
            "sunrise": daily.get("sunrise"),
            "sunset": daily.get("sunset"),
        }

        if env.test_mode:
            logger.info("🌤️ Successfully fetched weather data")
        return weather_data

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch weather data: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Error processing weather data: {str(e)}")
        return None
