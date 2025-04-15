# Felix & Pearl Bot 🐱🌤️

A sophisticated Discord bot duo that delivers daily messages about national days and weather updates, written from the perspective of two distinguished felines: Sir Felix Whiskersworth and Lady Pearl Weatherpaws. This project showcases advanced serverless architecture, AI integration, and precise timezone handling.

## 🚀 Key Features

The bot runs as an AWS Lambda function that triggers daily at 7 AM Eastern Time. It provides three sophisticated services:

- **Felix's National Days Service**: AI-powered daily messages about national days and observances, with personality-driven commentary
- **Pearl's Weather Service**: Intelligent weather updates with cat-themed observations and AI-generated insights
- **Birthday Service**: Personalized birthday messages with unique AI-generated content for each recipient

### Technical Capabilities

- **Precise Timezone Management**: Sophisticated DST handling ensures consistent 7 AM Eastern Time execution
- **Serverless Architecture**: Built on AWS Lambda with zero infrastructure maintenance
- **Scalable Design**: Handles multiple services in a single Lambda function
- **Production-Ready**: Comprehensive error handling, logging, and monitoring
- **AI Integration**: Claude AI powers natural language generation for unique, personality-driven content

## 🏗️ Technical Architecture

### Core Components

- **AWS Lambda**: Serverless execution environment
- **EventBridge**: Precise scheduling with automatic DST transitions
- **Systems Manager**: Secure configuration management
- **CloudWatch**: Comprehensive monitoring and logging
- **Claude AI**: Natural language generation for bot personalities

### Advanced DST Handling

The bot implements a sophisticated scheduling system that automatically adjusts for Daylight Saving Time:

```python
# Automatic DST transition handling
if current_month == 3 and 8 <= current_day <= 14:  # Second Sunday in March
    events.put_rule(
        Name="DailyScheduleEDT",
        ScheduleExpression="cron(0 11 * * ? *)",  # 7 AM EDT
        State="ENABLED"
    )
```

- **Automatic Transitions**: Seamlessly switches between EDT and EST
- **Zero Manual Intervention**: Fully automated DST handling
- **Consistent Execution**: Maintains 7 AM local time year-round

## 📁 Project Structure

```text
felix-and-pearl-bots/
├── src/
│   ├── lambda_function.py    # Main Lambda handler with all services
│   ├── dst_switch.py        # Sophisticated DST transition handling
│   ├── env_config.py        # Environment configuration management
│   ├── prompts.py           # AI prompt engineering
│   ├── bot_config.py        # Bot personality configurations
│   ├── birthday_config.py   # Birthday message handling
│   └── app.py              # Core application setup
├── scripts/
│   ├── build_lambda.py     # Lambda package builder
│   ├── deploy.py           # One-command deployment
│   └── test.py            # Testing and validation
├── template.yaml          # AWS SAM infrastructure
├── pyproject.toml        # Python project configuration
└── README.md            # Project documentation
```

## 🛠️ Development

### Quick Start

1. Clone and setup:

   ```bash
   git clone https://github.com/yourusername/felix-and-pearl-bots.git
   cd felix-and-pearl-bots
   poetry install
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Deploy:

   ```bash
   poetry run deploy
   ```

### Development Tools

- **Poetry**: Modern Python dependency management
- **AWS SAM**: Infrastructure as Code
- **Type Hints**: Full Python type annotation support
- **Logging**: Comprehensive CloudWatch integration

## 🔒 Security & Configuration

- **Secure Secrets**: Environment variables managed through AWS Systems Manager
- **API Keys**: Securely stored and never exposed in code
- **Test Mode**: Safe development environment with message suppression

## 📊 Monitoring

- **CloudWatch Logs**: Detailed execution tracking
- **Error Handling**: Comprehensive error logging and recovery
- **Performance Metrics**: Lambda execution monitoring

## 🎯 Technical Highlights

- **Single Lambda Function**: Efficiently handles multiple services
- **AI Integration**: Claude API for natural language generation
- **Timezone Precision**: Sophisticated DST handling
- **Serverless Architecture**: Zero infrastructure maintenance
- **Production-Ready**: Comprehensive error handling and monitoring

## 📝 License

MIT License - See LICENSE file for details
