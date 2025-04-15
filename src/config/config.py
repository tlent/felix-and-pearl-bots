from typing import Dict, List

# Bot configurations
BOT_NAMES = ["Felix", "Pearl"]

FELIX = {
    "name": "Felix",
    "full_name": "Felix the Fox",
    "description": (
        "a friendly and knowledgeable fox who loves sharing interesting facts "
        "about national days and celebrations. You have a playful personality "
        "and enjoy making people smile with your enthusiasm for special occasions."
    ),
}

PEARL = {
    "name": "Pearl",
    "full_name": "Pearl the Penguin",
    "description": (
        "a cheerful and observant penguin who loves sharing weather updates "
        "and making people feel cozy. You have a warm personality and enjoy "
        "helping others prepare for their day with weather information."
    ),
}

# Birthday configurations
BIRTHDAYS = {
    "01-01": {"name": "New Year", "type": "holiday"},
    "02-14": {"name": "Valentine's Day", "type": "holiday"},
    "03-17": {"name": "St. Patrick's Day", "type": "holiday"},
    "04-01": {"name": "April Fools' Day", "type": "holiday"},
    "05-05": {"name": "Cinco de Mayo", "type": "holiday"},
    "07-04": {"name": "Independence Day", "type": "holiday"},
    "10-31": {"name": "Halloween", "type": "holiday"},
    "12-25": {"name": "Christmas", "type": "holiday"},
    "12-31": {"name": "New Year's Eve", "type": "holiday"},
}


# Environment configurations
class EnvConfig:
    def __init__(self):
        self.test_mode = False
        self.anthropic_api_key = ""
        self.felix_webhook_url = ""
        self.pearl_webhook_url = ""
        self.weather_api_key = ""
        self.weather_lat = 0.0
        self.weather_lon = 0.0

    def load_from_env(self):
        """Load configuration from environment variables."""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.felix_webhook_url = os.getenv("FELIX_WEBHOOK_URL", "")
        self.pearl_webhook_url = os.getenv("PEARL_WEBHOOK_URL", "")
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "")
        self.weather_lat = float(os.getenv("WEATHER_LAT", "0.0"))
        self.weather_lon = float(os.getenv("WEATHER_LON", "0.0"))


# Initialize environment configuration
env = EnvConfig()
env.load_from_env()
