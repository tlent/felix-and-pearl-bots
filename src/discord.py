import requests
from typing import TypedDict

from config import logger, env, FELIX, PEARL


class WebhookResponse(TypedDict):
    content: str


def send_felix_message(content: str, test_mode: bool = False) -> bool:
    """Send a message as Felix."""
    return send_message(content, FELIX["name"], env.felix_webhook_url, test_mode)


def send_pearl_message(content: str, test_mode: bool = False) -> bool:
    """Send a message as Pearl."""
    return send_message(content, PEARL["name"], env.pearl_webhook_url, test_mode)


def send_message(
    content: str, character_name: str, webhook_url: str, test_mode: bool = False
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
            logger.info(f"💬 {character_name} would send: {content}")
            return True

        response = requests.post(webhook_url, json=WebhookResponse(content=content), timeout=10)
        response.raise_for_status()

        if env.test_mode:
            logger.info(f"💬 {character_name}'s message sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to send {character_name}'s message: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending {character_name}'s message: {str(e)}")
        return False
