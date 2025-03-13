# Felix Bot (Simplified)

A Discord bot that posts daily messages about national days and special occasions. The messages are written from the perspective of a cat named Sir Felix Whiskersworth.

## Features

- Fetches national days from a SQLite database
- Generates creative messages using Claude AI
- Posts daily messages to a Discord channel
- Minimal dependencies for better performance and smaller footprint

## Simplified Architecture

This version of Felix Bot has been optimized to use minimal dependencies while maintaining full functionality:

- Replaced async/await (tokio) with synchronous code using ureq
- Replaced time with chrono for date handling
- Replaced tracing with simple_logger for logging
- Uses anyhow for simplified error handling

## Deployment

### Prerequisites

- Docker installed on your Raspberry Pi
- Access to GitHub Container Registry
- Discord bot token
- Anthropic API key for Claude AI
- SQLite database with national days and birthdays

### Automatic Deployment

The bot is automatically deployed to your Raspberry Pi using GitHub Actions whenever changes are pushed to the main branch. The workflow:

1. Builds a Docker image
2. Pushes it to GitHub Container Registry
3. Connects to your Raspberry Pi via SSH
4. Pulls the latest image
5. Sets up a cron job to run the bot daily at 7 AM

### Manual Setup

If you need to set up the bot manually:

1. Install Docker on your Raspberry Pi
2. Create a directory for the bot:
   ```bash
   mkdir -p ~/felix-bot
   ```
3. Create an .env file with your API keys:
   ```bash
   echo "ANTHROPIC_API_KEY=your_key_here" > ~/felix-bot/.env
   echo "DISCORD_TOKEN=your_token_here" >> ~/felix-bot/.env
   ```
4. Copy your days.db file to the directory:
   ```bash
   cp /path/to/your/days.db ~/felix-bot/days.db
   ```
5. Pull the Docker image:
   ```bash
   docker pull ghcr.io/yourusername/felix-bot:latest
   ```
6. Set up a cron job to run the bot daily at 7 AM:
   ```bash
   (crontab -l 2>/dev/null; echo "0 7 * * * docker run --rm --env-file ~/felix-bot/.env -v ~/felix-bot/days.db:/app/days.db ghcr.io/yourusername/felix-bot:latest >> ~/felix-bot/felix-bot.log 2>&1") | crontab -
   ```

### Checking Logs

You can check the bot's logs at any time:

```bash
cat ~/felix-bot/felix-bot.log
```

### Testing the Bot

To run the bot manually:

```bash
docker run --rm --env-file ~/felix-bot/.env -v ~/felix-bot/days.db:/app/days.db ghcr.io/yourusername/felix-bot:latest
```

To run in test mode (verifies functionality without sending messages):

```bash
docker run --rm --env-file ~/felix-bot/.env -v ~/felix-bot/days.db:/app/days.db ghcr.io/yourusername/felix-bot:latest --test-mode
```

## Development

### Local Setup

1. Clone the repository
2. Install Rust and Cargo
3. Set up environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   export DISCORD_TOKEN=your_token_here
   ```
4. Make sure you have a days.db file in the project root
5. Run the bot:
   ```bash
   cargo run
   ```

### Building Locally

```bash
cargo build --release
```

### Building Docker Image Locally

```bash
docker build -t felix-bot .
``` 