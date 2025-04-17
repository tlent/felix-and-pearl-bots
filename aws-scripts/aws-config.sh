#!/usr/bin/env bash

# Default to 'default' profile if not set
export AWS_PROFILE="${AWS_PROFILE:-tlent-personal}"

# Default stack name if not set
export STACK_NAME="${STACK_NAME:-felix-pearl-bots}"

# Logical function name (used for local invocation and deployment)
export LOGICAL_FUNCTION_NAME="FelixPearlBotFunction"

# Load physical function name if available (used for AWS invocation)
if [ -f ".aws-sam/function-name.sh" ]; then
    source ".aws-sam/function-name.sh"
fi

# Secret name matches stack name by default
export SECRET_NAME="${STACK_NAME}-secrets"