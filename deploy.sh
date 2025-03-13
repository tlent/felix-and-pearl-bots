#!/bin/bash
set -e

REPO_OWNER=$1
VERSION_TAG=$2

# Store previous image for rollback
PREVIOUS_IMAGE=$(docker ps --filter "name=felix-bot" --format "{{.Image}}" 2>/dev/null || echo "none")
echo "Previous image: $PREVIOUS_IMAGE" > ~/felix-bot/rollback.txt

# Pull the latest image
docker pull ghcr.io/$REPO_OWNER/felix-bot:latest

# Create .env file if missing
[ ! -f ~/felix-bot/.env ] && {
  mkdir -p ~/felix-bot
  echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" > ~/felix-bot/.env
  echo "DISCORD_TOKEN=$DISCORD_TOKEN" >> ~/felix-bot/.env
}

# Stop and remove existing container
docker stop felix-bot 2>/dev/null || true
docker rm felix-bot 2>/dev/null || true

# Test the new image
if docker run --name felix-bot-test --rm --env-file ~/felix-bot/.env -v ~/felix-bot/days.db:/app/days.db ghcr.io/$REPO_OWNER/felix-bot:latest /usr/local/bin/felix-bot --test-mode; then
  # Set up cron job
  CRON_JOB="0 7 * * * docker run --rm --name felix-bot --env-file ~/felix-bot/.env -v ~/felix-bot/days.db:/app/days.db ghcr.io/$REPO_OWNER/felix-bot:latest /usr/local/bin/felix-bot >> ~/felix-bot/felix-bot.log 2>&1"
  if crontab -l 2>/dev/null | grep -q "felix-bot"; then
    (crontab -l 2>/dev/null | grep -v "felix-bot"; echo "$CRON_JOB") | crontab -
  else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  fi

  # Ensure log file exists
  touch ~/felix-bot/felix-bot.log
  echo "ghcr.io/$REPO_OWNER/felix-bot:$VERSION_TAG" > ~/felix-bot/current_version.txt
else
  echo "Test failed"
  exit 1
fi