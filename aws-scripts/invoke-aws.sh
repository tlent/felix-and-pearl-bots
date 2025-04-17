#!/usr/bin/env bash

source "aws-scripts/aws-config.sh"

mkdir -p .aws-sam/output

echo "🚀 Invoking function ${PHYSICAL_FUNCTION_NAME}..."
aws lambda invoke \
    --profile "${AWS_PROFILE}" \
    --function-name "${PHYSICAL_FUNCTION_NAME}" \
    .aws-sam/output/lambda-response.json

echo "📝 Response saved to .aws-sam/output/lambda-response.json"
