import logging
from datetime import datetime
from typing import TypedDict

import pytz
import requests

from src.config import Config

logger = logging.getLogger(__name__)

# Constants
PRECIPITATION_CHANCE_THRESHOLD = 0.2  # Minimum probability to show rain chance in forecast


class CurrentWeather(TypedDict):
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    wind_gust: float
    description: str
    clouds: int


class DailyWeather(TypedDict):
    high: float
    low: float
    feels_like: dict[str, float]  # day, night, eve, morn
    description: str
    pop: float  # probability of precipitation
    rain: float
    snow: float


class DailyForecast(TypedDict):
    date: datetime
    high: float
    low: float
    description: str
    pop: float
    rain: float
    snow: float


class WeatherData(TypedDict):
    current: CurrentWeather
    today: DailyWeather
    upcoming: list[DailyForecast]
    sunrise: datetime
    sunset: datetime
    moonrise: datetime
    moonset: datetime
    moon_phase: float


def get_weather(config: Config) -> WeatherData | None:
    """
    Get current weather data and daily forecast from OpenWeatherMap API.
    Returns WeatherData if successful, None if there's an error.
    """
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": config.weather_lat,
                "lon": config.weather_lon,
                "appid": config.weather_api_key,
                "units": "imperial",
                "exclude": "alerts,minutely,hourly",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        # Get timezone from API response
        tz = pytz.timezone(data["timezone"])

        # Convert timestamps to datetime objects
        current = data["current"]
        daily = data["daily"]  # Now using full daily array
        today = daily[0]  # First day's forecast

        # Process upcoming days (next 5 days)
        upcoming_days = []
        for day in daily[1:6]:  # Get next 5 days
            upcoming_days.append(
                DailyForecast(
                    date=datetime.fromtimestamp(day["dt"], tz=tz),
                    high=round(day["temp"]["max"]),
                    low=round(day["temp"]["min"]),
                    description=day["weather"][0]["description"],
                    pop=round(day["pop"], 1),
                    rain=round(day.get("rain", 0.0)),
                    snow=round(day.get("snow", 0.0)),
                )
            )

        # Format and structure the weather data to make it engaging and on-brand with Felix and Pearl
        return WeatherData(
            current=CurrentWeather(
                temp=round(current["temp"]),
                feels_like=round(current["feels_like"]),
                humidity=current["humidity"],
                wind_speed=round(current["wind_speed"]),
                wind_gust=round(current.get("wind_gust", 0.0)),
                description=current["weather"][0]["description"],
                clouds=current["clouds"],
            ),
            today=DailyWeather(
                high=round(today["temp"]["max"]),
                low=round(today["temp"]["min"]),
                feels_like={
                    "day": round(today["feels_like"]["day"]),
                    "night": round(today["feels_like"]["night"]),
                    "eve": round(today["feels_like"]["eve"]),
                    "morn": round(today["feels_like"]["morn"]),
                },
                description=today["weather"][0]["description"],
                pop=round(today["pop"], 1),
                rain=round(today.get("rain", 0.0)),
                snow=round(today.get("snow", 0.0)),
            ),
            upcoming=upcoming_days,
            sunrise=datetime.fromtimestamp(current["sunrise"], tz=tz),
            sunset=datetime.fromtimestamp(current["sunset"], tz=tz),
            moonrise=datetime.fromtimestamp(today["moonrise"], tz=tz),
            moonset=datetime.fromtimestamp(today["moonset"], tz=tz),
            moon_phase=today["moon_phase"],
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to fetch weather data: {e!s}")
        return None
    except Exception as e:
        logger.error(f"❌ Error processing weather data: {e!s}")
        return None
