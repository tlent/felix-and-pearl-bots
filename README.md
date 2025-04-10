# Felix & Pearl Bot

A Discord bot duo that posts daily messages about national days and weather updates, written from the perspective of two distinguished felines: Sir Felix Whiskersworth and Lady Pearl Weatherpaws.

## Overview

The bot runs as an AWS Lambda function that triggers daily at 7 AM Eastern Time. It provides three services:

- **Felix's National Days Service**: Fetches and shares daily national days and observances
- **Pearl's Weather Service**: Provides daily weather updates
- **Birthday Service**: Sends birthday messages on special occasions

### Key Features

- 🐱 Daily messages about national days and observances (Felix)
- 🌤️ Daily weather updates with cat-themed observations (Pearl)
- 🎂 Birthday messages for special occasions (both Felix and Pearl)
- 🤖 AI-generated content using Claude (used by both Felix and Pearl)
- ☁️ Serverless architecture using AWS Lambda
- ⏰ Automated daily execution at 7 AM Eastern Time with automatic DST handling

## Project Structure

```
felix-and-pearl-bots/
├── src/                  # Source code directory
│   ├── lambda_function.py    # Main Lambda function handling all services
│   ├── app.py               # Message handling and Discord integration
│   ├── birthday_config.py   # Birthday configuration
│   ├── bot_config.py       # General bot configuration
│   ├── dst_switch.py       # DST transition handling
│   └── prompts.py          # Bot prompts and templates
├── pyproject.toml      # Project configuration and dependencies
├── template.yaml       # AWS SAM template
├── .env.example       # Example environment variables template
├── env.json           # Local development environment variables
├── events/            # Test event files
└── README.md          # This file
```

## Setup

### Quick Start

1. Clone the repository
2. Install dependencies: `pip install .`
3. Copy `.env.example` to `.env` and fill in your values
4. Deploy: `sam build && sam deploy --guided`
5. Configure environment variables in AWS Systems Manager

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.7 or higher
- Anthropic API key (used by both bots)
- Discord webhook URL (used by both bots)
- OpenWeather API key (used by Pearl's weather service)

### Configuration Files

The project uses several configuration files:
- `pyproject.toml`: Project configuration and dependencies
- `.env.example`: Template for environment variables (copy to `.env` for local development)
- `env.json`: Local development environment variables for SAM CLI

### Environment Variables

The bot uses the following environment variables (configure in AWS Systems Manager or `.env`):
- `ANTHROPIC_API_KEY`: Your Anthropic API key (used by both bots)
- `FELIX_DISCORD_WEBHOOK_URL`: Discord webhook URL for Felix's messages
- `PEARL_DISCORD_WEBHOOK_URL`: Discord webhook URL for Pearl's messages
- `WEATHER_API_KEY`: OpenWeather API key (for Pearl's weather service)
- `WEATHER_LOCATION`: Location for weather updates (optional)
- `WEATHER_LAT`: Latitude for weather updates (required for OpenWeather One Call API 3.0)
- `WEATHER_LON`: Longitude for weather updates (required for OpenWeather One Call API 3.0)
- `BIRTHDAYS_CONFIG`: JSON string containing birthday configuration
- `TEST_MODE`: When set to 'true', prevents actual Discord messages from being sent (useful for testing)

## Birthday Configuration

Birthdays are configured in `birthday_config.py` without exposing personal information. The format is:
```python
BIRTHDAYS = {
    "MM-DD": {"name": "display_name"},
    # Example: "04-16": {"name": "Felix"}
}
```

When a birthday occurs:
1. Both Felix and Pearl send birthday messages
2. If it's a cat's own birthday, they also send a thank you message after receiving wishes from their sibling and family

## Development

```bash
# Install in development mode
pip install -e .

# Run locally
sam local invoke FelixPearlBotFunction --env-vars env.json --event events/test-event.json
```

## Monitoring

Logs can be viewed in CloudWatch Logs under the following log group:
- `/aws/lambda/FelixPearlBotFunction` - Main bot function

You can monitor the system through:
1. CloudWatch Logs for detailed execution logs and errors
2. CloudWatch Metrics for Lambda function invocations and errors
3. CloudWatch Alarms can be set up for:
   - High failure rates
   - Lambda function errors 

### Scheduling and DST Handling

The bot uses a sophisticated scheduling system to ensure consistent 7 AM Eastern Time execution:

1. **Daily Schedule**:
   - EDT Schedule: Runs at 7 AM EDT (11:00 UTC)
   - EST Schedule: Runs at 7 AM EST (12:00 UTC)

2. **DST Transition Handling**:
   - Automatic switching between EDT and EST schedules
   - DST switch function runs at midnight on transition days:
     - Second Sunday in March (spring forward)
     - First Sunday in November (fall back)
   - Only one schedule is active at a time to prevent duplicate executions

3. **Schedule Management**:
   - The DST switch function automatically enables/disables the appropriate schedule
   - Uses EventBridge rules for reliable scheduling
   - Maintains consistent 7 AM local time execution year-round 