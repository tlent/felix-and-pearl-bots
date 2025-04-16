import requests
from typing import TypedDict
import logging

from config import env, FELIX, PEARL

logger = logging.getLogger(__name__)


class WebhookResponse(TypedDict):
    content: str


def send_felix_message(content: str) -> bool:
    """Send a message as Felix."""
    return send_message(content, FELIX["name"], env.felix_webhook_url)


def send_pearl_message(content: str) -> bool:
    """Send a message as Pearl."""
    return send_message(content, PEARL["name"], env.pearl_webhook_url)


def send_message(
    content: str, character_name: str, webhook_url: str
) -> bool:
    """
    Send a message to Discord using the provided webhook URL.
    Returns True if successful, False otherwise.

    Args:
        content: The message content to send
        webhook_url: The Discord webhook URL to use
        character_name: The name of the character sending the message (for logging)
    """
    try:
        response = requests.post(webhook_url, json=WebhookResponse(content=content), timeout=10)
        response.raise_for_status()

        logger.info(f"💬 {character_name}'s message sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send {character_name}'s message: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending {character_name}'s message: {str(e)}")
        return False
