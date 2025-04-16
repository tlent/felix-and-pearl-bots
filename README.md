# Felix & Pearl Bot 🐱🌤️

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AWS Serverless](https://img.shields.io/badge/AWS-Serverless-orange.svg)](https://aws.amazon.com/serverless/)
[![Discord](https://img.shields.io/badge/Discord-Bot-blue.svg)](https://discord.com)

An AI-powered, zero-maintenance Discord bot duo delivering daily national day
highlights and weather updates from the unique perspective of two witty feline
personas. Built on a robust serverless architecture using AWS Lambda, it
features sophisticated Daylight Saving Time handling and seamless Claude AI
integration for smart, engaging messaging.

## 📖 Table of Contents

- [Features](#🚀-features)
- [Quick Start](#⚡-quick-start)
- [Project Structure](#📁-project-structure)
- [Architecture Overview](#🏗️-architecture-overview)
- [Security & Best Practices](#🔒-security--best-practices)
- [Development](#🛠️-development)
- [License](#📄-license)

---

## 🚀 Features

### Core Capabilities

- **Felix's National Days:**  
  Delivers daily highlights on national observances and quirky celebrations,
  featuring AI-generated commentary that adds a fun twist.

- **Pearl's Weather:**  
  Provides timely weather updates with cat-themed insights via the
  OpenWeatherMap API—keeping users informed and entertained.

- **Birthday Service:**  
  Sends personalized, AI-generated birthday messages to celebrate special days
  uniquely.

### Technical Highlights

- **Zero-Maintenance Architecture:**  
  Operates on a serverless stack with AWS Lambda and AWS SAM, ensuring minimal
  overhead and seamless scalability.

- **Sophisticated Daylight Saving Time Handling:**  
  Utilizes precise timezone detection and automated adjustments for Daylight
  Saving Time transitions, guaranteeing consistent scheduling (7 AM Eastern
  Time) even during spring forward or fall back.

- **Advanced AI Integration:**  
  Leverages Claude AI for natural language processing, ensuring engaging and
  context-aware messaging.

- **Secure Configuration:**  
  Manages sensitive data using AWS Parameter Store, ensuring secure and
  centralized configuration.

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/felix-and-pearl-bots.git
cd felix-and-pearl-bots
poetry install

# Configure (copy sample and add your keys)
cp env.json.sample env.json
# Edit env.json with your API keys and webhook URLs

# Run locally
sam build && sam local invoke FelixPearlBotFunction --env-vars env.json

# Deploy to AWS
sam build && sam deploy --guided
```

## 📁 Project Structure

```text
.
├── src/
│   ├── services/            # Core bot services
│   │   ├── birthdays.py     # Birthday messages
│   │   ├── national_days.py # National day updates
│   │   └── weather.py       # Weather updates
│   ├── ai.py               # Claude AI integration
│   ├── config.py           # Configuration
│   ├── discord.py          # Discord integration
│   ├── dst_switch.py       # DST handling
│   ├── lambda_function.py  # Main handler
│   └── prompts.py          # AI prompts
├── env.json                # Local config
├── pyproject.toml          # Poetry dependencies
├── requirements.txt        # Lambda dependencies
└── template.yaml           # AWS config
```

## 🏗️ Architecture Overview

### Serverless Stack

- **AWS Lambda:**  
  Fully serverless execution with automatic scaling, built-in fault tolerance,
  and zero infrastructure management.

- **Amazon EventBridge:**  
  Provides Daylight Saving Time-aware scheduling, ensuring messages are
  dispatched precisely when intended.

- **AWS Parameter Store:**  
  Handles secure storage of environment variables and secrets.

- **Amazon CloudWatch:**  
  Offers real-time monitoring and logging, vital for observability and
  debugging.

### Daylight Saving Time Handling

The project features a robust Daylight Saving Time system that:

- Automatically detects and adapts to Daylight Saving Time transitions.
- Maintains consistent execution at 7 AM Eastern Time.
- Accurately handles both spring-forward and fall-back transitions using
  Python's `zoneinfo` module.

## 🔒 Security & Best Practices

- **Secure Environment Management:**  
  All sensitive information (webhook URLs, API keys) is stored securely via AWS
  Parameter Store and referenced through environment variables.

- **Scalable and Maintainable:**  
  The serverless design minimizes infrastructure overhead and maintenance,
  allowing for rapid iteration and scalability.

## 🛠️ Development

### Prerequisites

- Python 3.13 or later
- AWS SAM (Serverless Application Model) CLI
- Configured AWS credentials
- Discord webhook URLs
- Claude AI API key
- OpenWeatherMap API key

### Local Setup

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Configure Environment:**

   Create `env.json` based on `env.json.sample` with your credentials and
   settings:

   ```json
   {
     "FelixPearlBotFunction": {
       "FELIX_DISCORD_WEBHOOK_URL": "your-felix-webhook-url",
       "PEARL_DISCORD_WEBHOOK_URL": "your-pearl-webhook-url",
       "ANTHROPIC_API_KEY": "your-claude-api-key",
       "WEATHER_API_KEY": "your-openweathermap-key",
       "WEATHER_LOCATION": "City,State,Country",
       "WEATHER_LAT": "latitude",
       "WEATHER_LON": "longitude",
       "BIRTHDAYS_CONFIG": "{\"MM-DD\": \"Name\"}",
       "TZ": "America/New_York",
       "TEST_MODE": "true"
     }
   }
   ```

4. **Run Locally:**

   Test the bot locally using the following:

   ```bash
   sam build && sam local invoke FelixPearlBotFunction --env-vars env.json
   ```

### Deployment

Build and deploy with:

```bash
sam build && sam deploy --guided
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
