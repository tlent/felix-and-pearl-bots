#!/usr/bin/env bash

# Source AWS configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/aws-config.sh"

# Get actual function name
FUNCTION_NAME=$(get_function_name)

aws lambda invoke \
    --profile "${AWS_PROFILE}" \
    --function-name "${FUNCTION_NAME}"
