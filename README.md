# Felix & Pearl Bot 🐱🌤️

An AI-powered, zero-maintenance Discord bot duo delivering daily national day
highlights and weather updates from the unique perspective of two witty feline
personas. Built on a robust serverless architecture using AWS Lambda, it
features sophisticated DST handling and seamless Claude AI integration for
smart, engaging messaging.

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

- **Sophisticated DST Handling:**  
  Utilizes precise timezone detection and automated adjustments for DST
  transitions, guaranteeing consistent scheduling (7 AM Eastern Time) even
  during spring forward or fall back.

- **Advanced AI Integration:**  
  Leverages Claude AI for natural language processing, ensuring engaging and
  context-aware messaging.

- **Secure Configuration:**  
  Manages sensitive data using AWS Parameter Store, ensuring secure and
  centralized configuration.

---

## 🏗️ Architecture Overview

### Serverless Stack

- **AWS Lambda:**  
  Fully serverless execution with automatic scaling, built-in fault tolerance,
  and zero infrastructure management.

- **Amazon EventBridge:**  
  Provides DST-aware scheduling, ensuring messages are dispatched precisely when
  intended.

- **AWS Parameter Store:**  
  Handles secure storage of environment variables and secrets.

- **Amazon CloudWatch:**  
  Offers real-time monitoring and logging, vital for observability and
  debugging.

### DST Handling

The project features a robust DST system that:

- Automatically detects and adapts to DST transitions.
- Maintains consistent execution at 7 AM Eastern Time.
- Accurately handles both spring-forward and fall-back transitions using
  Python's `zoneinfo` module.

---

## 🛠️ Development

### Prerequisites

- Python 3.13 or later
- AWS SAM CLI
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

---

## 📁 Project Structure

```text
.
├── src/
│   ├── services/
│   │   ├── birthdays.py      # Generates and schedules personalized birthday messages
│   │   ├── national_days.py  # Fetches and formats data for national days
│   │   └── weather.py        # Retrieves weather data and crafts cat-themed updates
│   ├── ai.py                 # Integrates Claude AI for natural, engaging messaging
│   ├── config.py             # Manages configuration and environment variables
│   ├── discord.py            # Handles Discord webhook communications
│   ├── dst_switch.py         # Detects and manages DST transitions accurately
│   ├── lambda_function.py    # The main Lambda handler orchestrating services
│   └── prompts.py            # Contains AI prompt templates and message formatting utilities
├── env.json                  # Environment configuration
├── pyproject.toml            # Poetry configuration for dependency management
├── requirements.txt          # Python dependencies for AWS Lambda deployment
└── template.yaml             # AWS SAM template for infrastructure deployment
```

---

## 🔒 Security & Best Practices

- **Secure Environment Management:**  
  All sensitive information (webhook URLs, API keys) is stored securely via AWS
  Parameter Store and referenced through environment variables.

- **Scalable and Maintainable:**  
  The serverless design minimizes infrastructure overhead and maintenance,
  allowing for rapid iteration and scalability.
