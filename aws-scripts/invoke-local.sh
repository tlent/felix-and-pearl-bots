#!/usr/bin/env bash

# Source AWS configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/aws-config.sh"

sam build

sam local invoke FelixPearlBotFunction \
    --profile "${AWS_PROFILE}" \
    --env-vars env.json
