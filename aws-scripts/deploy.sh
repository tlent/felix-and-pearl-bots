#!/usr/bin/env bash

# Source AWS configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/aws-config.sh"

sam build

# Extract parameters from env.json
PARAMS=$(jq -r '
  to_entries
  | map(
      .value
      | to_entries
      | map("ParameterKey=\(.key),ParameterValue=\(.value|tostring)")
    )
  | flatten
  | join(" ")
' env.json)

sam deploy \
  --profile "${AWS_PROFILE}" \
  --stack-name "${STACK_NAME}" \
  --parameter-overrides "${PARAMS}"
