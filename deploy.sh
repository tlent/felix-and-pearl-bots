#!/usr/bin/env bash

PROFILE="tlent-personal"
STACK_NAME="felix-pearl-bot"

# Get parameter overrides from env.json
PARAMS=$(jq -r '
  .FelixPearlBotFunction |
  to_entries |
  map("ParameterKey=\(.key),ParameterValue=\(.value|tostring)") |
  join(" ")
' env.json)

# Deploy the stack
sam deploy \
  --profile "$PROFILE" \
  --stack-name "$STACK_NAME" \
  --parameter-overrides "$PARAMS" 