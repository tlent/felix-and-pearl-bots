#!/usr/bin/env bash

source "aws-scripts/aws-config.sh"

# Validate secrets file exists
if [ ! -f "secrets.json" ]; then
    echo "❌ Error: secrets.json not found. Please create it from example.secrets.json"
    exit 1
fi

# Create or update secret
echo "🔐 Setting up AWS Secrets Manager..."
if ! aws secretsmanager describe-secret --secret-id "${SECRET_NAME}" > /dev/null 2>&1; then
    echo "Creating new secret ${SECRET_NAME}..."
    aws secretsmanager create-secret \
        --name "${SECRET_NAME}" \
        --secret-string file://secrets.json
else
    echo "Updating existing secret ${SECRET_NAME}..."
    aws secretsmanager update-secret \
        --secret-id "${SECRET_NAME}" \
        --secret-string file://secrets.json
fi

# Build and deploy
echo "🚀 Deploying to AWS..."
sam build && sam deploy \
    --profile "${AWS_PROFILE}" \
    --stack-name "${STACK_NAME}" \
    --capabilities CAPABILITY_IAM

# Get the actual function name
echo "📝 Getting function name..."
PHYSICAL_FUNCTION_NAME=$(aws cloudformation describe-stack-resource \
    --profile "${AWS_PROFILE}" \
    --stack-name "${STACK_NAME}" \
    --logical-resource-id "${LOGICAL_FUNCTION_NAME}" \
    --query 'StackResourceDetail.PhysicalResourceId' \
    --output text)

# Save the function name
echo "export PHYSICAL_FUNCTION_NAME=\"${PHYSICAL_FUNCTION_NAME}\"" > .aws-sam/function-name.sh
echo "✅ Physical function name saved: ${PHYSICAL_FUNCTION_NAME}"
