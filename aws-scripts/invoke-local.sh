#!/usr/bin/env bash

source "aws-scripts/aws-config.sh"

sam build

sam local invoke "${LOGICAL_FUNCTION_NAME}" \
    --profile "${AWS_PROFILE}"
