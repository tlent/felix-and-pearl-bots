#!/usr/bin/env bash

# Source AWS configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/aws-config.sh"

# Get the actual function name
FUNCTION_NAME=$(get_function_name)

if [ -z "$FUNCTION_NAME" ]; then
    echo "❌ Error: Could not find Felix & Pearl bot Lambda function"
    exit 1
fi

echo "🚀 Invoking Lambda function: $FUNCTION_NAME"
echo "----------------------------------------"

# Invoke the function and capture the response
if ! RESPONSE=$(aws lambda invoke \
    --profile "$AWS_PROFILE" \
    --function-name "$FUNCTION_NAME" \
    --log-type Tail /dev/null); then
    echo "❌ Function invocation failed"
    exit 1
fi

# Extract and decode the logs
echo "📝 Logs:"
echo "-----"
echo "$RESPONSE" | jq -r '.LogResult' | base64 -d
echo "✅ Function invoked successfully" 