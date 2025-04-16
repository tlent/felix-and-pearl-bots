import os
import json

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
        self.birthdays_config = json.loads(os.getenv("BIRTHDAYS_CONFIG"))


env = EnvConfig()
