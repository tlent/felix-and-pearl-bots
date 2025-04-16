#!/usr/bin/env bash

# AWS Configuration
export AWS_PROFILE="tlent-personal"
export STACK_NAME="felix-pearl-bot"

# Function name pattern (used to find the actual function name)
export FUNCTION_NAME_PATTERN="felix-pearl-bot-FelixPearlBotFunction"

# Get the actual function name from AWS
get_function_name() {
    aws lambda list-functions --profile "$AWS_PROFILE" | 
        jq -r ".Functions[] | select(.FunctionName | startswith(\"$FUNCTION_NAME_PATTERN\")) | .FunctionName"
} 