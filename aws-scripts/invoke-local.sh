#!/usr/bin/env bash

# Source AWS configuration
source "$(dirname "$0")/aws-config.sh"

echo "🔧 Building and invoking Lambda function locally..."
echo "----------------------------------------"

# Build and invoke the Lambda function locally
if ! sam build && sam local invoke FelixPearlBotFunction \
    --profile "$AWS_PROFILE" \
    --env-vars env.json; then
    echo "❌ Local invocation failed"
    exit 1
fi

echo "✅ Local invocation completed successfully" 