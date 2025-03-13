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
└── README.md           # This file
``` 