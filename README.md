# Felix Bot

A Discord bot that posts daily messages about national days and special occasions, written from the perspective of Sir Felix Whiskersworth, a distinguished feline.

## Overview

Felix Bot fetches data from a SQLite database of national days and birthdays, then uses Claude AI to craft creative messages that weave these events into a cohesive narrative. The result is a daily dose of feline wisdom and humor for your Discord server.

## Features

- Daily messages about national days and observances
- Birthday celebrations for special occasions
- AI-generated content using Claude
- Rich content with links to learn more about each national day
- Test mode for verifying functionality without sending messages
- Automated deployment to Raspberry Pi with scheduled daily execution

## Setup

1. **Environment Variables**

```
ANTHROPIC_API_KEY=your_anthropic_api_key
DISCORD_TOKEN=your_discord_bot_token
```

2. **Build and Run**

```bash
# Build
cargo build --release

# Run normally
cargo run --release

# Run in test mode
cargo run --release -- --test-mode
```

## Configuration

Key settings in `src/config.rs`:

| Setting | Default |
|---------|---------|
| Database path | `days.db` |
| Discord channel ID | `1218191951237742612` |
| Claude model | `claude-3-5-haiku-latest` |

## Database Schema

- **NationalDay**: `name`, `url`, `occurrence_2025` (YYYY-MM-DD)
- **Birthday**: `date` (YYYY-MM-DD), `description`

## Project Structure

```
felix-bot/
├── src/
│   ├── main.rs         # Application entry point
│   ├── lib.rs          # Library exports
│   ├── models.rs       # Data structures
│   ├── database.rs     # Database operations
│   ├── ai.rs           # Claude AI integration
│   ├── discord.rs      # Discord API integration
│   └── config.rs       # Configuration constants
├── days.db             # SQLite database
├── .github/workflows/  # CI/CD configuration
└── README.md           # This file
```

## Deployment

Felix Bot is automatically deployed to a Raspberry Pi 3 (arm64) using GitHub Actions. The deployment process includes:

1. Cross-compilation for ARM64 architecture
2. Building and pushing a Docker image to GitHub Container Registry
3. Deploying the image to the Raspberry Pi via SSH
4. Setting up a cron job to run the bot daily at 7:00 AM

### CI/CD Pipeline

The GitHub Actions workflow handles:

- Caching Rust dependencies for faster builds using Swatinem/rust-cache
- Building a Docker image for ARM64 architecture
- Testing the image before deployment
- Setting up or updating the cron job
- Automatic rollback in case of deployment failure

### Scheduled Execution

The bot is configured to run once daily at 7:00 AM using cron on the Raspberry Pi. This ensures:

- Regular daily updates without manual intervention
- Efficient resource usage by running only when needed
- Consistent timing for Discord server members

### Monitoring

Logs are stored in `~/felix-bot/felix-bot.log` on the Raspberry Pi for monitoring and troubleshooting.

## Development

For local development:

1. Clone the repository
2. Set up the required environment variables
3. Run in test mode to verify functionality without sending Discord messages

Changes pushed to the main branch will automatically trigger the deployment pipeline. 