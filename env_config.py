"""Environment configuration for Felix & Pearl Bot."""
import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

class EnvConfig:
    """Centralized environment configuration."""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_env()
            self._initialized = True

    def _load_env(self):
        """Load environment variables."""
        # Check if we're in test mode
        is_test = os.environ.get('TEST_MODE', 'false').lower() == 'true'
        
        # Load from appropriate .env file
        if is_test:
            load_dotenv('.env.test')
        else:
            load_dotenv()

        # Required variables with no defaults
        self.anthropic_api_key = self._get_required('ANTHROPIC_API_KEY')
        self.felix_webhook_url = self._get_required('FELIX_DISCORD_WEBHOOK_URL')
        self.pearl_webhook_url = self._get_required('PEARL_DISCORD_WEBHOOK_URL')
        self.weather_api_key = self._get_required('WEATHER_API_KEY')

        # Optional variables with defaults
        self.weather_location = os.environ.get('WEATHER_LOCATION', 'unknown')
        self.test_mode = is_test

        # Parse JSON config
        self.birthdays_config = self._parse_json_config(
            os.environ.get('BIRTHDAYS_CONFIG', '{}'),
            'BIRTHDAYS_CONFIG'
        )

    def _get_required(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.environ.get(key)
        if value is None:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    def _parse_json_config(self, json_str: str, key: str) -> Dict:
        """Parse a JSON configuration string."""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {key}: {e}")

    @property
    def weather_api_url(self) -> str:
        """Get the weather API URL."""
        return f"https://api.openweathermap.org/data/2.5/weather?q={self.weather_location}&appid={self.weather_api_key}&units=imperial"

    def override_for_testing(self, overrides: Dict[str, str]):
        """Override configuration for testing."""
        for key, value in overrides.items():
            setattr(self, key.lower(), value)
        self._initialized = True

# Global instance
env = EnvConfig() 