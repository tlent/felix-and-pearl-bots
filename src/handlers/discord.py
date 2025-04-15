import logging
from typing import Dict

import requests
from dotenv import load_dotenv

from src.config.config import env, FELIX, PEARL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def send_discord_message(
    content: str, webhook_url: str, character_name: str, test_mode: bool = False
) -> bool:
    """
    Send a message to Discord using the provided webhook URL.
    Returns True if successful, False otherwise.

    Args:
        content: The message content to send
        webhook_url: The Discord webhook URL to use
        character_name: The name of the character sending the message (for logging)
        test_mode: Whether we're in test mode
    """
    try:
        if test_mode:
            logger.info(f"Test mode: Would send {character_name}'s message: {content}")
            return True

        response = requests.post(webhook_url, json={"content": content}, timeout=10)

        if response.status_code == 204:
            logger.info(f"{character_name}'s message sent successfully")
            return True
        else:
            logger.error(
                f"Failed to send {character_name}'s message: HTTP {response.status_code}"
            )
            return False

    except Exception as e:
        logger.error(f"Error sending {character_name}'s message: {str(e)}")
        return False


def send_felix_message(content: str, test_mode: bool = False) -> bool:
    """Send a message using Felix's webhook."""
    return send_discord_message(
        content, env.felix_webhook_url, FELIX["name"], test_mode
    )


def send_pearl_message(content: str, test_mode: bool = False) -> bool:
    """Send a message using Pearl's webhook."""
    return send_discord_message(
        content, env.pearl_webhook_url, PEARL["name"], test_mode
    )
