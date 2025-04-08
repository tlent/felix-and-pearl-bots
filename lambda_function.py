import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import anthropic
import boto3
import pytz
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import configurations
from birthday_config import BIRTHDAYS
from bot_config import BOT_NAMES, BOT_BIRTHDAYS, FELIX, PEARL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize AWS clients
s3 = boto3.client('s3')
ssm = boto3.client('ssm')

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

# Discord webhooks for both bots
FELIX_WEBHOOK_URL = os.environ['FELIX_DISCORD_WEBHOOK_URL']
PEARL_WEBHOOK_URL = os.environ['PEARL_DISCORD_WEBHOOK_URL']

# Weather API configuration for Pearl's service
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']
WEATHER_LOCATION = os.environ.get('WEATHER_LOCATION', 'unknown')
WEATHER_API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={WEATHER_LOCATION}&appid={WEATHER_API_KEY}&units=imperial"

class NationalDay:
    """Represents a national day with its name, URL, and optional occurrence text."""
    def __init__(self, name: str, url: str, occurrence_text: Optional[str] = None):
        self.name = name
        self.url = url
        self.occurrence_text = occurrence_text

def is_test_mode(event: Dict) -> bool:
    """Check if we're in test mode based on event or environment variable."""
    test_mode = event.get('test_mode', False) or os.environ.get('TEST_MODE', 'false').lower() == 'true'
    logger.info(f"Test mode: {test_mode}")
    return test_mode

def check_birthdays(test_date: Optional[str] = None) -> List[Dict]:
    """
    Check if today is anyone's birthday.
    Args:
        test_date: Optional date string in MM-DD format for testing
    Returns a list of birthday entries for today.
    """
    if test_date:
        # Use the provided test date
        date_str = test_date
        logger.info(f"Using test date: {date_str}")
    else:
        # Get current date in Eastern Time
        eastern = pytz.timezone('America/New_York')
        now = datetime.now(eastern)
        date_str = now.strftime("%m-%d")
    
    # Check if today is anyone's birthday
    birthdays = []
    if date_str in BIRTHDAYS:
        birthdays.append(BIRTHDAYS[date_str])
        logger.info(f"Found birthday for {BIRTHDAYS[date_str]['name']}!")
    
    return birthdays

def generate_felix_birthday_message(birthday_info: Dict) -> str:
    """
    Generate a birthday message using Claude from Felix's perspective.
    Args:
        birthday_info: Dictionary containing birthday information
    """
    name = birthday_info['name']
    is_own_birthday = name == FELIX["name"]
    
    # Create the prompt for Claude
    if is_own_birthday:
        prompt = f"""You are {FELIX["full_name"]}, {FELIX["description"]}.
Today is your own birthday!

Please write a fun, engaging self-birthday message. Include:
1. A birthday greeting to yourself
2. A playful reference to something you enjoy
3. A fun birthday wish for yourself
4. A closing remark

Keep the tone light and playful, and make it sound like it's coming from a cat celebrating their own birthday. The message should be suitable for Discord."""
    else:
        prompt = f"""You are {FELIX["full_name"]}, {FELIX["description"]}.
Today is {name}'s birthday!

Please write a fun, engaging birthday message for {name}. Include:
1. A birthday greeting
2. A playful reference to something {name} might enjoy
3. A fun birthday wish
4. A closing remark

Keep the tone light and playful, and make it sound like it's coming from a cat. The message should be suitable for Discord and should be personal but not reveal any private information about {name}."""
    
    # Get response from Claude
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {FELIX['full_name']}, {FELIX['description']}.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def generate_pearl_birthday_message(birthday_info: Dict) -> str:
    """
    Generate a birthday message using Claude from Pearl's perspective.
    Args:
        birthday_info: Dictionary containing birthday information
    """
    name = birthday_info['name']
    is_own_birthday = name == PEARL["name"]
    
    # Create the prompt for Claude
    if is_own_birthday:
        prompt = f"""You are {PEARL["full_name"]}, {PEARL["description"]}.
Today is your own birthday!

Please write a fun, engaging self-birthday message. Include:
1. A birthday greeting to yourself
2. A playful reference to something you enjoy
3. A fun birthday wish for yourself
4. A closing remark

Keep the tone light and playful, and make it sound like it's coming from a cat celebrating their own birthday. The message should be suitable for Discord."""
    else:
        prompt = f"""You are {PEARL["full_name"]}, {PEARL["description"]}.
Today is {name}'s birthday!

Please write a fun, engaging birthday message for {name}. Include:
1. A birthday greeting
2. A playful reference to something {name} might enjoy
3. A fun birthday wish
4. A closing remark

Keep the tone light and playful, and make it sound like it's coming from a cat. The message should be suitable for Discord and should be personal but not reveal any private information about {name}."""
    
    # Get response from Claude
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {PEARL['full_name']}, {PEARL['description']}.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def generate_birthday_message(birthday_info: Dict, is_felix: bool = True) -> str:
    """
    Generate a birthday message using Claude.
    Args:
        birthday_info: Dictionary containing birthday information
        is_felix: Boolean indicating if the message is from Felix (True) or Pearl (False)
    """
    if is_felix:
        return generate_felix_birthday_message(birthday_info)
    else:
        return generate_pearl_birthday_message(birthday_info)

def generate_felix_thank_you_message(birthday_info: Dict) -> str:
    """
    Generate a thank you message for birthday wishes from Felix's perspective.
    Args:
        birthday_info: Dictionary containing birthday information
    """
    name = birthday_info['name']
    
    # Felix's character details
    character_full_name = "Sir Felix Whiskersworth"
    character_description = "a distinguished feline who loves to share interesting facts"
    
    prompt = f"""You are {character_full_name}, {character_description}.
Today is your birthday, and you just received birthday wishes from your sibling cat and your family!

Please write a sweet thank you message. Include:
1. A thank you to your sibling cat for their birthday wishes
2. A thank you to your family for their love and support
3. A playful remark about how lucky you are to have such wonderful family members
4. A closing remark

Keep the tone warm and appreciative, and make it sound like it's coming from a grateful cat. The message should be suitable for Discord."""
    
    # Get response from Claude
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {character_full_name}, {character_description}.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def generate_pearl_thank_you_message(birthday_info: Dict) -> str:
    """
    Generate a thank you message for birthday wishes from Pearl's perspective.
    Args:
        birthday_info: Dictionary containing birthday information
    """
    name = birthday_info['name']
    
    # Pearl's character details
    character_full_name = "Lady Pearl Weatherpaws"
    character_description = "a sophisticated cat who loves weather and is witty and playful"
    
    prompt = f"""You are {character_full_name}, {character_description}.
Today is your birthday, and you just received birthday wishes from your sibling cat and your family!

Please write a sweet thank you message. Include:
1. A thank you to your sibling cat for their birthday wishes
2. A thank you to your family for their love and support
3. A playful remark about how lucky you are to have such wonderful family members
4. A closing remark

Keep the tone warm and appreciative, and make it sound like it's coming from a grateful cat. The message should be suitable for Discord."""
    
    # Get response from Claude
    response = claude.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=1000,
        temperature=0.7,
        system=f"You are {character_full_name}, {character_description}.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def generate_thank_you_message(birthday_info: Dict, is_felix: bool = True) -> str:
    """
    Generate a thank you message for birthday wishes.
    Args:
        birthday_info: Dictionary containing birthday information
        is_felix: Boolean indicating if the message is from Felix (True) or Pearl (False)
    """
    if is_felix:
        return generate_felix_thank_you_message(birthday_info)
    else:
        return generate_pearl_thank_you_message(birthday_info)

def get_national_days() -> Tuple[List[NationalDay], Optional[str]]:
    """
    Scrapes national days from nationaldaycalendar.com.
    Returns a tuple of (list of national days, error message if any).
    """
    try:
        # Get current date in Eastern Time
        eastern = pytz.timezone('America/New_York')
        now = datetime.now(eastern)
        month = now.strftime('%B').lower()
        day = now.day
        
        # Construct URL
        url = f"https://www.nationaldaycalendar.com/{month}/{month}-{day}"
        logger.info(f"Fetching national days from: {url}")
        
        # Make request with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            national_days = []
            
            # Find all national day cards
            cards = soup.select('.m-card--header a')
            logger.info(f"Found {len(cards)} total cards")
            
            # Words/phrases that indicate a non-national day entry
            excluded_phrases = [
                'birthdays and events',
                'on this day',
                'historical events',
                'celebrity birthdays'
            ]
            
            for card in cards:
                try:
                    text = card.get_text(strip=True)
                    logger.debug(f"Processing card: {text}")
                    
                    # Skip if this is not a national day
                    text_lower = text.lower()
                    if any(phrase in text_lower for phrase in excluded_phrases):
                        logger.debug(f"Skipping non-national day entry: {text}")
                        continue
                        
                    # Skip if it doesn't start with "NATIONAL" or "INTERNATIONAL"
                    if not (text.upper().startswith('NATIONAL') or text.upper().startswith('INTERNATIONAL')):
                        logger.debug(f"Skipping non-national/international day: {text}")
                        continue
                    
                    # Parse name and occurrence text
                    name = text
                    occurrence_text = None
                    
                    # Try different separators
                    for separator in [' | ', ' - ', '| ', '- ']:
                        if separator in text:
                            name, occurrence_text = text.split(separator, 1)
                            break
                    
                    national_days.append(NationalDay(
                        name=name.strip(),
                        url=card.get('href', '#'),
                        occurrence_text=occurrence_text.strip() if occurrence_text else None
                    ))
                except (AttributeError, KeyError) as e:
                    logger.warning(f"Error processing card: {str(e)}")
                    continue
            
            if not national_days:
                logger.warning("No national days found on the page")
                return [], "No national days found on the page"
                
            logger.info("Found National Days:")
            for day in national_days:
                logger.info(f"- {day.name}" + (f" ({day.occurrence_text})" if day.occurrence_text else ""))
                
            return national_days, None
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            return [], f"Error parsing HTML: {str(e)}"
            
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return [], f"Failed to fetch data: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [], f"Unexpected error: {str(e)}"

def get_weather() -> Optional[Dict]:
    """Fetch weather data"""
    try:
        logger.info("Fetching weather from OpenWeather API")
        response = requests.get(WEATHER_API_URL)
        response.raise_for_status()
        weather_data = response.json()
        
        # Extract relevant weather information
        weather = {
            'temperature': round(weather_data['main']['temp']),
            'feels_like': round(weather_data['main']['feels_like']),
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': round(weather_data['wind']['speed']),
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%I:%M %p'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%I:%M %p')
        }
        
        logger.info("Weather Data:")
        for key, value in weather.items():
            logger.info(f"{key}: {value}")
        
        return weather
    except (requests.RequestException, KeyError, ValueError, TypeError, AttributeError) as e:
        # These are non-critical errors that shouldn't fail the entire lambda
        logger.error(f"Error fetching weather (non-critical): {str(e)}")
        return None
    except Exception as e:
        # Unexpected errors should be logged but not crash the lambda
        logger.error(f"Unexpected error fetching weather (non-critical): {str(e)}")
        return None

def generate_weather_message(weather_data: Dict) -> Optional[str]:
    """Generate a weather message using Claude from Pearl's perspective."""
    try:
        logger.info("Generating weather message")
        
        # Get location from environment variable
        location = os.environ.get('WEATHER_LOCATION', 'unknown')
        
        # Create the prompt for Claude
        prompt = f"""You are Lady Pearl Weatherpaws, a sophisticated and witty cat who loves to talk about the weather. 
        Generate a fun, engaging message about today's weather in {location}. 
        Use cat-themed weather observations and include some playful weather-related cat facts.
        
        Weather data:
        - Temperature: {weather_data['temperature']}°F (feels like {weather_data['feels_like']}°F)
        - Conditions: {weather_data['description']}
        - Humidity: {weather_data['humidity']}%
        - Wind Speed: {weather_data['wind_speed']} mph
        - Sunrise: {weather_data['sunrise']}
        - Sunset: {weather_data['sunset']}
        
        Keep the message under 1000 characters and make it fun and engaging."""
        
        # Generate message using Claude
        message = claude.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1000,
            temperature=0.7,
            system="You are Lady Pearl Weatherpaws, a sophisticated cat who loves weather. Be witty and playful.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        weather_message = message.content[0].text
        logger.info("Generated Weather Message:")
        logger.info(weather_message)
        
        return weather_message
    except Exception as e:
        # Weather message generation errors are non-critical
        logger.error(f"Error generating weather message (non-critical): {str(e)}")
        return None

def generate_message(national_days: List[NationalDay]) -> Optional[str]:
    """Generate a message using Claude about the national days from Felix's perspective."""
    try:
        # Format the national days data
        days_text = "\n".join([
            f"- {day.name}" + (f" ({day.occurrence_text})" if day.occurrence_text else "")
            for day in national_days
        ])
        
        logger.info("National Days Found:")
        logger.info(days_text)
        
        # Create the prompt for Claude
        prompt = f"""You are Sir Felix Whiskersworth, a distinguished feline who loves to share interesting facts about national days. 
Today's national days are:

{days_text}

Please write a fun, engaging message about these national days. Include:
1. A greeting
2. A brief mention of each national day
3. A fun fact or interesting tidbit about one of the days
4. A closing remark

Keep the tone light and playful, and make it sound like it's coming from a cat. The message should be suitable for Discord."""

        # Get response from Claude
        response = claude.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1000,
            temperature=0.7,
            system="You are Sir Felix Whiskersworth, a distinguished feline who loves to share interesting facts about national days.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        # National days message generation errors are non-critical
        logger.error(f"Error generating national days message (non-critical): {str(e)}")
        return None

def send_discord_message(content: str, webhook_url: str, test_mode: bool = False) -> bool:
    """
    Send a message to Discord using the provided webhook URL.
    Returns True if successful, False otherwise.
    
    Args:
        content: The message content to send
        webhook_url: The Discord webhook URL
        test_mode: Whether we're in test mode
    """
    try:
        if test_mode:
            logger.info(f"Test mode: Would send message: {content}")
            return True
            
        response = requests.post(
            webhook_url,
            json={'content': content},
            timeout=10
        )
        
        if response.status_code == 204:
            logger.info("Message sent successfully")
            return True
        else:
            logger.error(f"Failed to send message: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

def lambda_handler(event, context):
    """
    Main Lambda handler for Felix & Pearl Bot.
    Handles national days, weather updates, and birthday messages.
    """
    try:
        # Check if we're in test mode
        test_mode = is_test_mode(event)
        logger.info("Starting Felix & Pearl Bot execution")
        
        # Check for birthdays
        birthdays = check_birthdays()
        if birthdays:
            logger.info("Processing birthdays")
            for birthday in birthdays:
                # Generate and send Felix's message
                felix_message = generate_felix_birthday_message(birthday)
                if not send_discord_message(felix_message, FELIX_WEBHOOK_URL, test_mode):
                    logger.error("Failed to send Felix's birthday message")
                
                # Generate and send Pearl's message
                pearl_message = generate_pearl_birthday_message(birthday)
                if not send_discord_message(pearl_message, PEARL_WEBHOOK_URL, test_mode):
                    logger.error("Failed to send Pearl's birthday message")
                
                # If it's one of the bots' birthdays, send thank you messages
                if birthday['name'] in BOT_NAMES:
                    thank_you_message = generate_felix_thank_you_message(birthday)
                    if not send_discord_message(thank_you_message, FELIX_WEBHOOK_URL, test_mode):
                        logger.error("Failed to send Felix's thank you message")
                    
                    thank_you_message = generate_pearl_thank_you_message(birthday)
                    if not send_discord_message(thank_you_message, PEARL_WEBHOOK_URL, test_mode):
                        logger.error("Failed to send Pearl's thank you message")
        
        # Get national days
        national_days, error = get_national_days()
        if error:
            logger.error(f"Error getting national days: {error}")
        elif national_days:
            # Generate and send Felix's message
            felix_message = generate_message(national_days)
            if felix_message and not send_discord_message(felix_message, FELIX_WEBHOOK_URL, test_mode):
                logger.error("Failed to send Felix's national days message")
        
        # Get weather
        weather_data = get_weather()
        if weather_data:
            # Generate and send Pearl's message
            pearl_message = generate_weather_message(weather_data)
            if pearl_message and not send_discord_message(pearl_message, PEARL_WEBHOOK_URL, test_mode):
                logger.error("Failed to send Pearl's weather message")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Felix & Pearl Bot execution completed')
        }
        
    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        } 