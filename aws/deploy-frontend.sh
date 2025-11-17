#!/bin/bash

# Frontend Deployment Script
# Deploys React frontend to S3 and CloudFront

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_NAME="missing-roles-agent"
ENVIRONMENT="${ENVIRONMENT:-production}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo -e "${GREEN}Deploying Frontend to AWS${NC}"

# Get S3 bucket name from CloudFormation
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='FrontendBucketName'].OutputValue" \
    --output text)

ALB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ALBEndpoint'].OutputValue" \
    --output text)

echo -e "${YELLOW}S3 Bucket: ${BUCKET_NAME}${NC}"
echo -e "${YELLOW}API Endpoint: http://${ALB_ENDPOINT}${NC}"

# Build frontend
echo -e "\n${GREEN}[1/3] Building frontend...${NC}"
cd frontend
npm install
VITE_API_URL="http://${ALB_ENDPOINT}/api" npm run build

# Upload to S3
echo -e "\n${GREEN}[2/3] Uploading to S3...${NC}"
aws s3 sync dist/ "s3://${BUCKET_NAME}/" \
    --delete \
    --region "${AWS_REGION}"

# Invalidate CloudFront cache
echo -e "\n${GREEN}[3/3] Invalidating CloudFront cache...${NC}"
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
    --output text)

if [ -n "${DISTRIBUTION_ID}" ]; then
    aws cloudfront create-invalidation \
        --distribution-id "${DISTRIBUTION_ID}" \
        --paths "/*" \
        --region "${AWS_REGION}"
    echo -e "${GREEN}CloudFront cache invalidated${NC}"
else
    echo -e "${YELLOW}CloudFront distribution ID not found. Skipping cache invalidation.${NC}"
fi

CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
    --output text)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Frontend Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Frontend URL: https://${CLOUDFRONT_URL}"
echo -e "S3 Bucket: ${BUCKET_NAME}"

cd ..

