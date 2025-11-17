# AWS Deployment Files

This directory contains all files needed to deploy the Missing Job Roles AI Agent to AWS.

## 📁 Directory Structure

```
aws/
├── cloudformation/
│   └── infrastructure.yaml      # CloudFormation template for AWS infrastructure
├── ecs/
│   ├── task-definition.json     # ECS task definition template
│   └── service-definition.json  # ECS service definition template
├── deploy.sh                    # Linux/Mac deployment script
├── deploy.ps1                   # Windows PowerShell deployment script
├── deploy-frontend.sh           # Linux/Mac frontend deployment script
├── deploy-frontend.ps1          # Windows PowerShell frontend deployment script
├── run-migrations.sh            # Linux/Mac migration script
├── run-migrations.ps1           # Windows PowerShell migration script
└── README.md                    # This file
```

## 🚀 Quick Start

### For Linux/Mac:

```bash
# 1. Set environment variables
export ENVIRONMENT=production
export AWS_REGION=us-east-1
export DB_PASSWORD="your-secure-password"
export DB_USERNAME="admin"

# 2. Make scripts executable
chmod +x aws/*.sh

# 3. Deploy
./aws/deploy.sh
```

### For Windows (PowerShell):

```powershell
# 1. Set environment variables
$env:ENVIRONMENT = "production"
$env:AWS_REGION = "us-east-1"
$env:DB_PASSWORD = "your-secure-password"
$env:DB_USERNAME = "admin"

# 2. Deploy
.\aws\deploy.ps1
```

## 📋 Files Description

### CloudFormation Template (`cloudformation/infrastructure.yaml`)

Defines the complete AWS infrastructure:
- VPC with public/private subnets
- RDS MySQL database
- ECS Fargate cluster
- Application Load Balancer
- S3 bucket for frontend
- CloudFront distribution
- Security groups
- IAM roles
- Secrets Manager

### ECS Task Definition (`ecs/task-definition.json`)

Template for ECS task definition. The deployment script automatically replaces placeholders with actual values:
- `REPLACE_WITH_TASK_EXECUTION_ROLE_ARN`
- `REPLACE_WITH_TASK_ROLE_ARN`
- `REPLACE_WITH_ECR_IMAGE_URI`
- `REPLACE_WITH_SECRETS_ARN`

### ECS Service Definition (`ecs/service-definition.json`)

Template for ECS service. The deployment script replaces:
- `REPLACE_WITH_CLUSTER_NAME`
- `REPLACE_WITH_PRIVATE_SUBNET_1`
- `REPLACE_WITH_PRIVATE_SUBNET_2`
- `REPLACE_WITH_ECS_SECURITY_GROUP`
- `REPLACE_WITH_TARGET_GROUP_ARN`

### Deployment Scripts

**`deploy.sh` / `deploy.ps1`**: Main deployment script that:
1. Deploys CloudFormation stack
2. Creates ECR repository
3. Builds and pushes Docker image
4. Registers ECS task definition
5. Creates/updates ECS service

**`deploy-frontend.sh` / `deploy-frontend.ps1`**: Frontend deployment that:
1. Builds React frontend
2. Uploads to S3
3. Invalidates CloudFront cache

**`run-migrations.sh` / `run-migrations.ps1`**: Runs Django migrations on ECS

## 🔧 Customization

### Change Region

Set `AWS_REGION` environment variable:
```bash
export AWS_REGION=eu-west-1  # Linux/Mac
$env:AWS_REGION = "eu-west-1"  # Windows
```

### Change Environment

Set `ENVIRONMENT` environment variable:
```bash
export ENVIRONMENT=staging  # Linux/Mac
$env:ENVIRONMENT = "staging"  # Windows
```

### Modify Infrastructure

Edit `cloudformation/infrastructure.yaml` and redeploy:
```bash
./aws/deploy.sh  # or .\aws\deploy.ps1
```

### Modify ECS Configuration

Edit `ecs/task-definition.json` or `ecs/service-definition.json` and redeploy.

## 📝 Notes

- All scripts require AWS CLI to be configured
- Docker must be installed and running
- CloudFormation stack creation takes 15-20 minutes
- Make sure to update secrets in Secrets Manager after deployment
- Run migrations after first deployment

## 🔗 Related Documentation

See `../AWS_DEPLOYMENT.md` for complete deployment guide.

