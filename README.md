# Felix & Pearl Bot 🐱🌤️

A Discord bot duo that delivers daily messages about national days and weather updates, written from the perspective of two cats: Sir Felix Whiskersworth and Lady Pearl Weatherpaws. This project uses serverless architecture, AI integration, and handles timezone changes.

## 🚀 Key Features

The bot runs as an AWS Lambda function that triggers daily at 7 AM Eastern Time. It provides three services:

- **Felix's National Days Service**: Daily messages about national days and observances, with commentary using Claude AI
- **Pearl's Weather Service**: Weather updates with cat-themed observations, using OpenWeatherMap API
- **Birthday Service**: Birthday messages with AI-generated content for each recipient

### Technical Capabilities

- **Timezone Management**: DST handling ensures 7 AM Eastern Time execution
- **Serverless Architecture**: Built on AWS Lambda with AWS SAM for deployment
- **AI Integration**: Claude AI for natural language generation

## 🏗️ Technical Architecture

### Core Components

- **AWS Lambda**: Serverless execution environment
- **EventBridge**: Scheduling with DST transitions
- **Parameter Store**: Secure storage of API keys and configuration
- **CloudWatch**: Basic monitoring and logging
- **Claude AI**: Natural language generation

### DST Handling

The bot handles Daylight Saving Time through dedicated DST management code:

```python
def is_dst_change_day() -> bool:
    """Check if today is a DST change day."""
    now = get_current_time()

    # Check for spring forward (second Sunday in March)
    if now.month == 3:
        first_day = datetime(now.year, 3, 1, tzinfo=ZoneInfo("America/New_York"))
        days_until_sunday = (6 - first_day.weekday()) % 7
        second_sunday = first_day + timedelta(days=days_until_sunday + 7)
        return now.date() == second_sunday.date()

    # Check for fall back (first Sunday in November)
    if now.month == 11:
        first_day = datetime(now.year, 11, 1, tzinfo=ZoneInfo("America/New_York"))
        days_until_sunday = (6 - first_day.weekday()) % 7
        first_sunday = first_day + timedelta(days=days_until_sunday)
        return now.date() == first_sunday.date()

    return False
```

- **DST Handling**: Uses zoneinfo module for timezone calculations
- **Automatic Transitions**: Switches between EDT and EST schedules
- **Consistent Execution**: Maintains 7 AM local time year-round

## 📁 Project Structure

```text
felix-and-pearl-bots/
├── src/
│   ├── lambda_function.py    # Main Lambda handler
│   ├── services/
│   │   ├── birthdays.py      # Birthday service
│   │   ├── national_days.py  # National days service
│   │   ├── weather.py        # Weather service
│   │   └── dst_switch.py     # DST transition handling
│   ├── handlers/
│   │   ├── discord.py        # Discord message handling
│   │   └── ai.py             # AI message generation
│   └── config/
│       ├── config.py         # Configuration
│       └── prompts.py        # AI prompts
├── scripts/
│   ├── build_lambda.py       # Lambda package builder
│   ├── deploy.py             # Deployment script
│   └── test.py               # Testing script
├── template.yaml             # AWS SAM template
├── pyproject.toml            # Python project config
└── .env.example              # Environment variable template
```

## 🛠️ Development

### Poetry Scripts

The project uses Poetry for dependency management and automation. Here are the available scripts:

```bash
# Install dependencies
poetry install

# Run tests
poetry run test

# Build Lambda package
poetry run build

# Deploy to AWS
poetry run deploy
```

Each script is configured in `pyproject.toml` and handles specific development tasks. The deploy script requires AWS credentials configured in your environment.

### Development Tools

- **Poetry**: Python dependency management
- **AWS SAM**: Infrastructure as Code
- **Logging**: Basic CloudWatch integration

## 🔒 Security & Configuration

- **Secrets Management**: API keys and sensitive data stored in AWS Parameter Store
- **Test Mode**: Development environment with message suppression

## 🎯 Technical Highlights

- **Modular Design**: Services and handlers separation
- **AI Integration**: Claude API for message generation
- **Timezone Handling**: Robust DST management
- **Serverless**: AWS Lambda deployment with AWS SAM
