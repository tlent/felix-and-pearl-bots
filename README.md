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
- ⏰ Automated daily execution at 7 AM Eastern Time (adjusts for EDT/EST)

## Project Structure

```
felix-pearl-bot/
├── lambda_function.py    # Main Lambda function handling all services
├── app.py                # Message handling
├── birthday_config.py    # Birthday configuration (no personal information)
├── requirements.txt      # Python dependencies
├── template.yaml         # AWS SAM template
├── tests/               # Test directory
│   ├── test_lambda_function.py
│   └── test_app.py
└── README.md            # This file
```

## Setup

### Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Deploy: `sam build && sam deploy --guided`
4. Configure environment variables in AWS Systems Manager

### Prerequisites

- AWS CLI installed and configured
- AWS SAM CLI installed
- Python 3.12
- Anthropic API key (used by both bots)
- Discord webhook URL (used by both bots)
- OpenWeather API key (used by Pearl's weather service)

### Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Deploy using SAM
sam build
sam deploy --guided
```

During the guided deployment, you'll need to provide:
- Anthropic API key (for both bots' message generation)
- Discord webhook URL (for both bots' messages)
- OpenWeather API key (for Pearl's weather service)
- Weather location

## Configuration

The bot uses the following environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key (used by both bots)
- `FELIX_DISCORD_WEBHOOK_URL`: Discord webhook URL for Felix's messages
- `PEARL_DISCORD_WEBHOOK_URL`: Discord webhook URL for Pearl's messages
- `WEATHER_API_KEY`: OpenWeather API key (for Pearl's weather service)
- `WEATHER_LOCATION`: Location for weather updates (optional)
- `BIRTHDAYS_CONFIG`: JSON string containing birthday configuration

## Birthday Configuration

Birthdays are configured in `birthday_config.py` without exposing personal information. The format is:
```python
BIRTHDAYS = {
    "MM-DD": {"name": "display_name", "is_own_birthday": boolean},
    # Example: "04-16": {"name": "Felix", "is_own_birthday": true}
}
```

When a birthday occurs:
1. Both Felix and Pearl send birthday messages
2. If it's a cat's own birthday, they also send a thank you message after receiving wishes from their sibling and family

## Development

```bash
# Run locally
sam local invoke FelixPearlBotFunction
```

## Testing

The project includes a comprehensive test suite with both unit and integration tests. The tests use pytest and include mocked AWS services using moto.

### Test Structure
```
tests/
├── unit/                  # Unit tests
│   ├── test_app.py       # Tests for app.py
│   ├── test_env_config.py
│   ├── test_message_generation.py
│   └── test_birthday_config.py
├── integration/          # Integration tests
├── conftest.py          # Shared test fixtures
└── .env.test            # Test environment variables
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/

# Run with coverage report
python -m pytest --cov=. tests/
```

### Test Environment

The tests use a separate test environment file (`tests/.env.test`) and mock external services:
- AWS services are mocked using moto
- External API calls (OpenWeather, Anthropic) are mocked
- Discord webhook calls are intercepted and verified
- DateTime operations use a fixed test date

### Local Testing

For testing the Lambda function locally with test mode:
```bash
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