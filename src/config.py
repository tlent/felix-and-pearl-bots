import os
import logging

# Configure logging once for the entire application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot names and identities
FELIX = {
    "name": "Felix",
    "full_name": "Sir Felix Whiskersworth",
    "description": "a distinguished feline who loves to share interesting facts",
    "birthday": "07-16",
}

PEARL = {
    "name": "Pearl",
    "full_name": "Lady Pearl Weatherpaws",
    "description": "a sophisticated cat who loves weather and is witty and playful",
    "birthday": "04-23",
}


class EnvConfig:
    def __init__(self):
        self.test_mode = os.getenv("TEST_MODE")
        self.felix_webhook_url = os.getenv("FELIX_WEBHOOK_URL")
        self.pearl_webhook_url = os.getenv("PEARL_WEBHOOK_URL")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.weather_location = os.getenv("WEATHER_LOCATION")
        self.weather_lat = float(os.getenv("WEATHER_LAT"))
        self.weather_lon = float(os.getenv("WEATHER_LON"))

        # Parse birthdays from simple format: "MM-DD:Name,MM-DD:Name"
        birthdays_str = os.getenv("BIRTHDAYS_CONFIG", "")
        self.birthdays_config = {}

        if not birthdays_str:
            return

        try:
            for entry in birthdays_str.split(","):
                entry = entry.strip()
                if not entry:
                    continue

                if ":" not in entry:
                    raise ValueError(
                        f"Invalid birthday entry format: '{entry}'. Expected 'MM-DD:Name'"
                    )

                date, name = entry.split(":", 1)
                date = date.strip()
                name = name.strip()

                if not date or not name:
                    raise ValueError(f"Empty date or name in entry: '{entry}'")

                # Validate date format (MM-DD)
                try:
                    month, day = date.split("-")
                    if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
                        raise ValueError(
                            f"Invalid date in entry: '{entry}'. "
                            "Month must be 1-12, day must be 1-31"
                        )
                except ValueError as e:
                    raise ValueError(
                        f"Invalid date format in entry: '{entry}'. Expected MM-DD"
                    ) from e

                self.birthdays_config[date] = name

        except Exception as e:
            raise ValueError(
                f"Error parsing BIRTHDAYS_CONFIG: {str(e)}. "
                "Format should be 'MM-DD:Name,MM-DD:Name'"
            ) from e


env = EnvConfig()
