"""
Bot configuration for Felix & Pearl Bot.
This file contains the core bot identities and their properties.
"""

# Bot names and identities
FELIX = {
    "name": "Felix",
    "full_name": "Sir Felix Whiskersworth",
    "description": "a distinguished feline who loves to share interesting facts",
    "birthday": "07-16"  # MM-DD format
}

PEARL = {
    "name": "Pearl",
    "full_name": "Lady Pearl Weatherpaws",
    "description": "a sophisticated cat who loves weather and is witty and playful",
    "birthday": "04-23"  # MM-DD format
}

# Set of bot names for easy lookup
BOT_NAMES = {FELIX["name"], PEARL["name"]}

# Bot birthdays for easy lookup
BOT_BIRTHDAYS = {
    FELIX["birthday"]: FELIX["name"],
    PEARL["birthday"]: PEARL["name"]
} 