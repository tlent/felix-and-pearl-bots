#!/usr/bin/env bash

# Source AWS configuration
source "$(dirname "$0")/aws-config.sh"

echo "🚀 Deploying Felix & Pearl Bot..."
echo "----------------------------------------"

# Build the application
echo "🔨 Building the application..."
if ! sam build; then
  echo "❌ Build failed"
  exit 1
fi

# Get parameter overrides from env.json
PARAMS=$(jq -r '
  .FelixPearlBotFunction |
  to_entries |
  map("ParameterKey=\(.key),ParameterValue=\(.value|tostring)") |
  join(" ")
' env.json)

# Deploy the stack
if ! sam deploy \
  --profile "$AWS_PROFILE" \
  --stack-name "$STACK_NAME" \
  --parameter-overrides "$PARAMS"; then
  echo "❌ Deployment failed"
  exit 1
fi

echo "✅ Deployment completed successfully" 