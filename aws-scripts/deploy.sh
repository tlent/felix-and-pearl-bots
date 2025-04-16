#!/usr/bin/env bash
set -e

source "$(dirname "$0")/aws-config.sh"

echo "🚀 Deploying Felix & Pearl Bot..."
echo "----------------------------------------"

echo "🔨 Building the application..."
sam build

echo "📦 Loading parameters from env.json..."
PARAMS=$(jq -r 'to_entries | map("ParameterKey=\(.key),ParameterValue=\(.value|tostring)") | join(" ")' env.json)

echo "📤 Deploying to AWS..."
sam deploy \
  --profile "$AWS_PROFILE" \
  --stack-name "$STACK_NAME" \
  --parameter-overrides "$PARAMS"
