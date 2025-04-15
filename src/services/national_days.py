import logging
from datetime import datetime
from typing import List, Optional, Tuple

import pytz
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NationalDay:
    """Represents a national day with its name, URL, and optional occurrence text."""

    def __init__(self, name: str, url: str, occurrence_text: Optional[str] = None):
        self.name = name
        self.url = url
        self.occurrence_text = occurrence_text


def get_national_days() -> Tuple[List[NationalDay], Optional[str]]:
    """
    Scrapes national days from nationaldaycalendar.com.
    Returns a tuple of (list of national days, error message if any).
    """
    try:
        # Get current date in Eastern Time
        eastern = pytz.timezone("America/New_York")
        now = datetime.now(eastern)
        month = now.strftime("%B").lower()
        day = now.day

        # Construct URL
        url = f"https://www.nationaldaycalendar.com/{month}/{month}-{day}"
        logger.info(f"Fetching national days from: {url}")

        # Make request with proper headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            national_days = []

            # Find all national day cards
            cards = soup.select(".m-card--header a")
            logger.info(f"Found {len(cards)} total cards")

            for card in cards:
                name = card.text.strip()
                url = card["href"]
                national_days.append(NationalDay(name=name, url=url))

            return national_days, None

        except Exception as e:
            error_msg = f"Error parsing national days HTML: {str(e)}"
            logger.error(error_msg)
            return [], error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching national days: {str(e)}"
        logger.error(error_msg)
        return [], error_msg
