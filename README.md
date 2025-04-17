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

- [🚀 Features](#-features)
- [⚡ Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [🏗️ Architecture Overview](#%EF%B8%8F-architecture-overview)
- [🔒 Security & Best Practices](#-security--best-practices)
- [🛠️ Development](#%EF%B8%8F-development)
- [🔮 Future Enhancements](#-future-enhancements)
- [📄 License](#-license)

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
  Manages sensitive data using AWS Secrets Manager with automatic secret
  rotation and IAM-based access control, ensuring secure and centralized
  configuration management.

- **Streamlined Deployment:**  
  Features a simplified deployment process with AWS SAM, making it easy to
  deploy updates and manage infrastructure as code.

## ⚡ Quick Start

```bash
# Clone and install
git clone https://github.com/tlent/felix-and-pearl-bots.git
cd felix-and-pearl-bots
poetry install

# Configure secrets (copy sample and add your keys)
cp example.secrets.json secrets.json
# Edit secrets.json with your API keys and webhook URLs

# Optional: Configure AWS (defaults to 'default' profile)
export AWS_PROFILE="your-profile"  # Optional
export STACK_NAME="your-stack"     # Optional

# Run locally to test
./aws-scripts/invoke-local.sh

# Deploy to AWS (creates/updates secrets automatically)
./aws-scripts/deploy.sh
```

That's it! The deployment script will automatically:

- Create or update your AWS Secrets Manager secret
- Build and deploy your application
- Set up all necessary AWS resources

## 📁 Project Structure

```text
.
├── aws-scripts/          # AWS deployment and invocation scripts
│   ├── aws-config.sh     # Common AWS configuration
│   ├── deploy.sh         # Deployment script
│   ├── invoke-aws.sh     # AWS Lambda invocation script
│   └── invoke-local.sh   # Local Lambda invocation script
├── src/
│   ├── services/            # Core service modules for bot features
│   │   ├── birthdays.py     # Birthday detection and AI-powered message generation
│   │   ├── national_days.py # Web scraping and processing of national holidays
│   │   └── weather.py       # Weather API integration and forecast processing
│   ├── ai.py               # Claude AI integration and personality-driven messaging
│   ├── config.py           # Environment, service, and character configuration
│   ├── discord.py          # Discord webhook and message handling
│   ├── dst_switch.py       # Timezone, DST, and AWS EventBridge management
│   ├── lambda_function.py  # AWS Lambda entry point and service coordination
│   ├── logging.py          # Structured logging configuration
│   └── prompts.py          # AI prompt templates and personality settings
├── example.secrets.json    # Example secrets configuration
├── secrets.json           # Local secrets configuration (gitignored)
├── pyproject.toml         # Poetry package management
├── requirements.txt       # AWS Lambda runtime dependencies
└── template.yaml          # AWS SAM infrastructure definition
```

## 🏗️ Architecture Overview

### Serverless Stack

- **AWS Lambda:**  
  Fully serverless execution with automatic scaling, built-in fault tolerance,
  and zero infrastructure management.

- **Amazon EventBridge:**  
  Provides Daylight Saving Time-aware scheduling, ensuring messages are
  dispatched precisely when intended.

- **AWS Secrets Manager:**  
  Handles secure storage of environment variables and secrets, with automatic
  rotation and access control.

- **Amazon CloudWatch:**  
  Offers real-time monitoring and logging, vital for observability and
  debugging.

### Daylight Saving Time Handling

The project features a robust Daylight Saving Time system that:

- Maintains consistent 7 AM Eastern Time execution through dual EventBridge
  schedules:
  - `DailyScheduleEDT`: 7 AM EDT (11:00 UTC)
  - `DailyScheduleEST`: 7 AM EST (12:00 UTC)
- Automatically switches between schedules via a dedicated DST check function
  that runs daily at 10:00 UTC
- Accurately handles both spring-forward and fall-back transitions using
  Python's `zoneinfo` module
- Ensures zero downtime during DST transitions through automated schedule
  management

## 🔒 Security & Best Practices

- **Secure Secrets Management:**  
  All sensitive information (webhook URLs, API keys) is stored securely in AWS
  Secrets Manager, ensuring centralized and encrypted storage of credentials.

- **Local Development Security:**  
  Local development uses a `secrets.json` file (gitignored) that mirrors the
  structure of AWS Secrets Manager, allowing for secure local testing without
  exposing credentials.

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

3. **Configure Secrets:**

   Create `secrets.json` based on `example.secrets.json` with your credentials
   and settings:

   ```json
   {
     "FELIX_DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/your-felix-webhook-id/your-felix-webhook-token",
     "PEARL_DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/your-pearl-webhook-id/your-pearl-webhook-token",
     "ANTHROPIC_API_KEY": "sk-ant-api03-your-claude-api-key",
     "WEATHER_API_KEY": "your-openweathermap-api-key",
     "WEATHER_LOCATION": "City,State,Country",
     "WEATHER_LAT": "0.0",
     "WEATHER_LON": "0.0",
     "BIRTHDAYS_CONFIG": "MMDD:Name,MMDD:Name",
     "TZ": "America/New_York"
   }
   ```

4. **Set Up AWS Secrets Manager:**

   Create a secret in AWS Secrets Manager with your configuration:

   ```bash
   aws secretsmanager create-secret --name FelixPearlBotSecrets --secret-string file://secrets.json
   ```

5. **Run Locally:**

   Test the bot locally using the following:

   ```bash
   ./aws-scripts/invoke-local.sh
   ```

### Deployment

The project uses AWS SAM for streamlined deployment with helper scripts:

```bash
# Deploy to AWS
./aws-scripts/deploy.sh

# Invoke the deployed function manually
./aws-scripts/invoke-aws.sh
```

The deployment process automatically handles:

- Infrastructure provisioning
- Environment variable management
- IAM role configuration
- CloudWatch logging setup
- DST-aware scheduling

Note: Before using the AWS scripts, configure your AWS profile and stack name in
`aws-scripts/aws-config.sh`.

## 🔮 Future Enhancements

### Testing Infrastructure

- Implement comprehensive test suite covering core functionality
- Add unit tests for service modules, DST handling, and AI integration
- Include integration tests for AWS services and Discord webhooks
- Set up CI/CD pipeline with automated testing

### Message Generation Pipeline

- Decouple message generation from delivery for better reliability
- Implement pre-generation system with AWS S3 storage
- Add preview functionality with email notifications
- Create approval workflow with regenerate capability
- Enable batch generation of messages for multiple days

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.
