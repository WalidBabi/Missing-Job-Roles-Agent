# AWS Deployment Script for Windows PowerShell
# Missing Job Roles Agent - AWS Deployment

$ErrorActionPreference = "Stop"

# Configuration
$PROJECT_NAME = "missing-roles-agent"
$ENVIRONMENT = if ($env:ENVIRONMENT) { $env:ENVIRONMENT } else { "production" }
$AWS_REGION = if ($env:AWS_REGION) { $env:AWS_REGION } else { "us-east-1" }
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)

# ECR Repository
$ECR_REPOSITORY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-backend"

Write-Host "Starting AWS Deployment for ${PROJECT_NAME} (${ENVIRONMENT})" -ForegroundColor Green
Write-Host "AWS Account: ${AWS_ACCOUNT_ID}" -ForegroundColor Yellow
Write-Host "AWS Region: ${AWS_REGION}" -ForegroundColor Yellow

# Check AWS CLI
Write-Host "`n[1/8] Checking AWS CLI..." -ForegroundColor Green
try {
    aws --version | Out-Null
} catch {
    Write-Host "AWS CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "`n[2/8] Checking Docker..." -ForegroundColor Green
try {
    docker --version | Out-Null
} catch {
    Write-Host "Docker is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Deploy CloudFormation Stack
Write-Host "`n[3/8] Deploying CloudFormation Infrastructure..." -ForegroundColor Green
$STACK_NAME = "${PROJECT_NAME}-${ENVIRONMENT}-infrastructure"

$stackExists = aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" 2>$null
if ($stackExists) {
    Write-Host "Stack exists, updating..." -ForegroundColor Yellow
    aws cloudformation update-stack `
        --stack-name "${STACK_NAME}" `
        --template-body file://aws/cloudformation/infrastructure.yaml `
        --parameters `
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" `
            ParameterKey=Environment,ParameterValue="${ENVIRONMENT}" `
            ParameterKey=DatabasePassword,ParameterValue="${env:DB_PASSWORD}" `
            ParameterKey=DatabaseUsername,ParameterValue="${env:DB_USERNAME}" `
        --capabilities CAPABILITY_IAM `
        --region "${AWS_REGION}"
    
    Write-Host "Waiting for stack update to complete..." -ForegroundColor Yellow
    aws cloudformation wait stack-update-complete --stack-name "${STACK_NAME}" --region "${AWS_REGION}"
} else {
    Write-Host "Stack does not exist, creating..." -ForegroundColor Yellow
    aws cloudformation create-stack `
        --stack-name "${STACK_NAME}" `
        --template-body file://aws/cloudformation/infrastructure.yaml `
        --parameters `
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" `
            ParameterKey=Environment,ParameterValue="${ENVIRONMENT}" `
            ParameterKey=DatabasePassword,ParameterValue="${env:DB_PASSWORD}" `
            ParameterKey=DatabaseUsername,ParameterValue="${env:DB_USERNAME}" `
        --capabilities CAPABILITY_IAM `
        --region "${AWS_REGION}"
    
    Write-Host "Waiting for stack creation to complete..." -ForegroundColor Yellow
    aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}" --region "${AWS_REGION}"
}

Write-Host "Infrastructure deployed successfully!" -ForegroundColor Green

# Get stack outputs
Write-Host "`n[4/8] Retrieving stack outputs..." -ForegroundColor Green
$CLUSTER_NAME = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" --output text)
$TASK_EXECUTION_ROLE = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ECSTaskExecutionRoleArn'].OutputValue" --output text)
$TASK_ROLE = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ECSTaskRoleArn'].OutputValue" --output text)
$SECRETS_ARN = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='SecretsManagerArn'].OutputValue" --output text)
$TARGET_GROUP_ARN = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ALBTargetGroupArn'].OutputValue" --output text)
$PRIVATE_SUBNETS = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='PrivateSubnetIds'].OutputValue" --output text)
$PRIVATE_SUBNET_1 = $PRIVATE_SUBNETS.Split(',')[0]
$PRIVATE_SUBNET_2 = $PRIVATE_SUBNETS.Split(',')[1]
$VPC_ID = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='VPCId'].OutputValue" --output text)
$ECS_SG = (aws ec2 describe-security-groups --filters "Name=vpc-id,Values=${VPC_ID}" "Name=group-name,Values=${PROJECT_NAME}-${ENVIRONMENT}-ecs-sg" --region "${AWS_REGION}" --query "SecurityGroups[0].GroupId" --output text)

# Create ECR Repository
Write-Host "`n[5/8] Setting up ECR Repository..." -ForegroundColor Green
$repoExists = aws ecr describe-repositories --repository-names "${PROJECT_NAME}-backend" --region "${AWS_REGION}" 2>$null
if (-not $repoExists) {
    Write-Host "Creating ECR repository..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name "${PROJECT_NAME}-backend" --region "${AWS_REGION}" --image-scanning-configuration scanOnPush=true
}

# Build and Push Docker Image
Write-Host "`n[6/8] Building and Pushing Docker Image..." -ForegroundColor Green
Write-Host "Logging in to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REPOSITORY}"

Write-Host "Building Docker image..." -ForegroundColor Yellow
docker build -t "${PROJECT_NAME}-backend:latest" .

Write-Host "Tagging image..." -ForegroundColor Yellow
docker tag "${PROJECT_NAME}-backend:latest" "${ECR_REPOSITORY}:latest"

Write-Host "Pushing image to ECR..." -ForegroundColor Yellow
docker push "${ECR_REPOSITORY}:latest"

$IMAGE_URI = "${ECR_REPOSITORY}:latest"
Write-Host "Image pushed: ${IMAGE_URI}" -ForegroundColor Green

# Update Secrets Manager
Write-Host "`n[7/8] Updating Secrets Manager..." -ForegroundColor Green
Write-Host "Please update secrets in AWS Secrets Manager: ${SECRETS_ARN}" -ForegroundColor Yellow
Write-Host "Required secrets: SECRET_KEY, DB_HOST, DB_USER, DB_PASSWORD, OPENAI_API_KEY, ANTHROPIC_API_KEY" -ForegroundColor Yellow

# Register ECS Task Definition
Write-Host "`n[8/8] Registering ECS Task Definition..." -ForegroundColor Green
$TASK_DEF_CONTENT = Get-Content aws/ecs/task-definition.json -Raw
$TASK_DEF_CONTENT = $TASK_DEF_CONTENT -replace "REPLACE_WITH_TASK_EXECUTION_ROLE_ARN", $TASK_EXECUTION_ROLE
$TASK_DEF_CONTENT = $TASK_DEF_CONTENT -replace "REPLACE_WITH_TASK_ROLE_ARN", $TASK_ROLE
$TASK_DEF_CONTENT = $TASK_DEF_CONTENT -replace "REPLACE_WITH_ECR_IMAGE_URI", $IMAGE_URI
$TASK_DEF_CONTENT = $TASK_DEF_CONTENT -replace "REPLACE_WITH_SECRETS_ARN", $SECRETS_ARN
$TASK_DEF_FILE = New-TemporaryFile
$TASK_DEF_CONTENT | Out-File -FilePath $TASK_DEF_FILE.FullName -Encoding utf8

aws ecs register-task-definition --cli-input-json "file://$($TASK_DEF_FILE.FullName)" --region "${AWS_REGION}"
Remove-Item $TASK_DEF_FILE.FullName

# Create or Update ECS Service
Write-Host "`n[9/9] Creating/Updating ECS Service..." -ForegroundColor Green
$SERVICE_DEF_CONTENT = Get-Content aws/ecs/service-definition.json -Raw
$SERVICE_DEF_CONTENT = $SERVICE_DEF_CONTENT -replace "REPLACE_WITH_CLUSTER_NAME", $CLUSTER_NAME
$SERVICE_DEF_CONTENT = $SERVICE_DEF_CONTENT -replace "REPLACE_WITH_PRIVATE_SUBNET_1", $PRIVATE_SUBNET_1
$SERVICE_DEF_CONTENT = $SERVICE_DEF_CONTENT -replace "REPLACE_WITH_PRIVATE_SUBNET_2", $PRIVATE_SUBNET_2
$SERVICE_DEF_CONTENT = $SERVICE_DEF_CONTENT -replace "REPLACE_WITH_ECS_SECURITY_GROUP", $ECS_SG
$SERVICE_DEF_CONTENT = $SERVICE_DEF_CONTENT -replace "REPLACE_WITH_TARGET_GROUP_ARN", $TARGET_GROUP_ARN
$SERVICE_DEF_FILE = New-TemporaryFile
$SERVICE_DEF_CONTENT | Out-File -FilePath $SERVICE_DEF_FILE.FullName -Encoding utf8

$serviceExists = aws ecs describe-services --cluster "${CLUSTER_NAME}" --services "${PROJECT_NAME}-backend-service" --region "${AWS_REGION}" --query "services[0].status" --output text 2>$null
if ($serviceExists -eq "ACTIVE") {
    Write-Host "Service exists, updating..." -ForegroundColor Yellow
    aws ecs update-service --cluster "${CLUSTER_NAME}" --service "${PROJECT_NAME}-backend-service" --task-definition "${PROJECT_NAME}-backend" --region "${AWS_REGION}" --force-new-deployment
} else {
    Write-Host "Service does not exist, creating..." -ForegroundColor Yellow
    aws ecs create-service --cli-input-json "file://$($SERVICE_DEF_FILE.FullName)" --region "${AWS_REGION}"
}
Remove-Item $SERVICE_DEF_FILE.FullName

# Get ALB endpoint
$ALB_ENDPOINT = (aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='ALBEndpoint'].OutputValue" --output text)

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Backend API: http://${ALB_ENDPOINT}"
Write-Host "Cluster: ${CLUSTER_NAME}"
Write-Host "Image: ${IMAGE_URI}"
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Update secrets in AWS Secrets Manager: ${SECRETS_ARN}"
Write-Host "2. Run database migrations: .\aws\run-migrations.ps1"
Write-Host "3. Deploy frontend: .\aws\deploy-frontend.ps1"
Write-Host "4. Update CORS settings in Django with frontend URL"

