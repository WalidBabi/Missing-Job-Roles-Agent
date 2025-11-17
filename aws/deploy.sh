#!/bin/bash

# AWS Deployment Script for Missing Job Roles Agent
# This script deploys the application to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="missing-roles-agent"
ENVIRONMENT="${ENVIRONMENT:-production}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR Repository
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-backend"

echo -e "${GREEN}Starting AWS Deployment for ${PROJECT_NAME} (${ENVIRONMENT})${NC}"
echo -e "${YELLOW}AWS Account: ${AWS_ACCOUNT_ID}${NC}"
echo -e "${YELLOW}AWS Region: ${AWS_REGION}${NC}"

# Step 1: Check AWS CLI
echo -e "\n${GREEN}[1/8] Checking AWS CLI...${NC}"
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Step 2: Check Docker
echo -e "\n${GREEN}[2/8] Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install it first.${NC}"
    exit 1
fi

# Step 3: Deploy CloudFormation Stack
echo -e "\n${GREEN}[3/8] Deploying CloudFormation Infrastructure...${NC}"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"

# Check if stack exists
if aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" &> /dev/null; then
    echo -e "${YELLOW}Stack exists, updating...${NC}"
    aws cloudformation update-stack \
        --stack-name "${STACK_NAME}" \
        --template-body file://aws/cloudformation/infrastructure.yaml \
        --parameters \
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" \
            ParameterKey=Environment,ParameterValue="${ENVIRONMENT}" \
            ParameterKey=DatabasePassword,ParameterValue="${DB_PASSWORD}" \
            ParameterKey=DatabaseUsername,ParameterValue="${DB_USERNAME:-admin}" \
        --capabilities CAPABILITY_IAM \
        --region "${AWS_REGION}"
    
    echo -e "${YELLOW}Waiting for stack update to complete...${NC}"
    aws cloudformation wait stack-update-complete \
        --stack-name "${STACK_NAME}" \
        --region "${AWS_REGION}"
else
    echo -e "${YELLOW}Stack does not exist, creating...${NC}"
    aws cloudformation create-stack \
        --stack-name "${STACK_NAME}" \
        --template-body file://aws/cloudformation/infrastructure.yaml \
        --parameters \
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" \
            ParameterKey=Environment,ParameterValue="${ENVIRONMENT}" \
            ParameterKey=DatabasePassword,ParameterValue="${DB_PASSWORD}" \
            ParameterKey=DatabaseUsername,ParameterValue="${DB_USERNAME:-admin}" \
        --capabilities CAPABILITY_IAM \
        --region "${AWS_REGION}"
    
    echo -e "${YELLOW}Waiting for stack creation to complete...${NC}"
    aws cloudformation wait stack-create-complete \
        --stack-name "${STACK_NAME}" \
        --region "${AWS_REGION}"
fi

echo -e "${GREEN}Infrastructure deployed successfully!${NC}"

# Step 4: Get stack outputs
echo -e "\n${GREEN}[4/8] Retrieving stack outputs...${NC}"
CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" \
    --output text)

TASK_EXECUTION_ROLE=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ECSTaskExecutionRoleArn'].OutputValue" \
    --output text)

TASK_ROLE=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ECSTaskRoleArn'].OutputValue" \
    --output text)

SECRETS_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='SecretsManagerArn'].OutputValue" \
    --output text)

TARGET_GROUP_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ALBTargetGroupArn'].OutputValue" \
    --output text)

PRIVATE_SUBNET_1=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnetIds'].OutputValue" \
    --output text | cut -d',' -f1)

PRIVATE_SUBNET_2=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnetIds'].OutputValue" \
    --output text | cut -d',' -f2)

VPC_ID=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='VPCId'].OutputValue" \
    --output text)

ECS_SG=$(aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=group-name,Values=${PROJECT_NAME}-${ENVIRONMENT}-ecs-sg" \
    --region "${AWS_REGION}" \
    --query "SecurityGroups[0].GroupId" \
    --output text)

# Step 5: Create ECR Repository
echo -e "\n${GREEN}[5/8] Setting up ECR Repository...${NC}"
if ! aws ecr describe-repositories --repository-names "${PROJECT_NAME}-backend" --region "${AWS_REGION}" &> /dev/null; then
    echo -e "${YELLOW}Creating ECR repository...${NC}"
    aws ecr create-repository \
        --repository-name "${PROJECT_NAME}-backend" \
        --region "${AWS_REGION}" \
        --image-scanning-configuration scanOnPush=true
fi

# Step 6: Build and Push Docker Image
echo -e "\n${GREEN}[6/8] Building and Pushing Docker Image...${NC}"
echo -e "${YELLOW}Logging in to ECR...${NC}"
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REPOSITORY}"

echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t "${PROJECT_NAME}-backend:latest" .

echo -e "${YELLOW}Tagging image...${NC}"
docker tag "${PROJECT_NAME}-backend:latest" "${ECR_REPOSITORY}:latest"

echo -e "${YELLOW}Pushing image to ECR...${NC}"
docker push "${ECR_REPOSITORY}:latest"

IMAGE_URI="${ECR_REPOSITORY}:latest"
echo -e "${GREEN}Image pushed: ${IMAGE_URI}${NC}"

# Step 7: Update Secrets Manager
echo -e "\n${GREEN}[7/8] Updating Secrets Manager...${NC}"
echo -e "${YELLOW}Please update secrets in AWS Secrets Manager: ${SECRETS_ARN}${NC}"
echo -e "${YELLOW}Required secrets: SECRET_KEY, DB_HOST, DB_USER, DB_PASSWORD, OPENAI_API_KEY, ANTHROPIC_API_KEY${NC}"

# Step 8: Register ECS Task Definition
echo -e "\n${GREEN}[8/8] Registering ECS Task Definition...${NC}"

# Create task definition file with actual values
TASK_DEF_FILE=$(mktemp)
cat aws/ecs/task-definition.json | \
    sed "s|REPLACE_WITH_TASK_EXECUTION_ROLE_ARN|${TASK_EXECUTION_ROLE}|g" | \
    sed "s|REPLACE_WITH_TASK_ROLE_ARN|${TASK_ROLE}|g" | \
    sed "s|REPLACE_WITH_ECR_IMAGE_URI|${IMAGE_URI}|g" | \
    sed "s|REPLACE_WITH_SECRETS_ARN|${SECRETS_ARN}|g" > "${TASK_DEF_FILE}"

aws ecs register-task-definition \
    --cli-input-json file://"${TASK_DEF_FILE}" \
    --region "${AWS_REGION}"

rm "${TASK_DEF_FILE}"

# Step 9: Create or Update ECS Service
echo -e "\n${GREEN}[9/9] Creating/Updating ECS Service...${NC}"

# Create service definition file with actual values
SERVICE_DEF_FILE=$(mktemp)
cat aws/ecs/service-definition.json | \
    sed "s|REPLACE_WITH_CLUSTER_NAME|${CLUSTER_NAME}|g" | \
    sed "s|REPLACE_WITH_PRIVATE_SUBNET_1|${PRIVATE_SUBNET_1}|g" | \
    sed "s|REPLACE_WITH_PRIVATE_SUBNET_2|${PRIVATE_SUBNET_2}|g" | \
    sed "s|REPLACE_WITH_ECS_SECURITY_GROUP|${ECS_SG}|g" | \
    sed "s|REPLACE_WITH_TARGET_GROUP_ARN|${TARGET_GROUP_ARN}|g" > "${SERVICE_DEF_FILE}"

if aws ecs describe-services \
    --cluster "${CLUSTER_NAME}" \
    --services "${PROJECT_NAME}-backend-service" \
    --region "${AWS_REGION}" \
    --query "services[0].status" \
    --output text 2>/dev/null | grep -q "ACTIVE"; then
    echo -e "${YELLOW}Service exists, updating...${NC}"
    aws ecs update-service \
        --cluster "${CLUSTER_NAME}" \
        --service "${PROJECT_NAME}-backend-service" \
        --task-definition "${PROJECT_NAME}-backend" \
        --region "${AWS_REGION}" \
        --force-new-deployment
else
    echo -e "${YELLOW}Service does not exist, creating...${NC}"
    aws ecs create-service \
        --cli-input-json file://"${SERVICE_DEF_FILE}" \
        --region "${AWS_REGION}"
fi

rm "${SERVICE_DEF_FILE}"

# Get ALB endpoint
ALB_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${AWS_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ALBEndpoint'].OutputValue" \
    --output text)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Backend API: http://${ALB_ENDPOINT}"
echo -e "Cluster: ${CLUSTER_NAME}"
echo -e "Image: ${IMAGE_URI}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Update secrets in AWS Secrets Manager: ${SECRETS_ARN}"
echo -e "2. Run database migrations: aws ecs run-task ..."
echo -e "3. Deploy frontend to S3/CloudFront"
echo -e "4. Update CORS settings in Django with frontend URL"

