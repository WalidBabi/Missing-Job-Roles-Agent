# Quick Start: Deploy to AWS

This is a condensed guide for deploying to AWS. For detailed documentation, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).

## Deployment Options

### Option 1: Deploy to Existing EC2 Instance (Quick)

If you have an EC2 instance with IP `16.171.237.146`:

```bash
# Linux/Mac
export EC2_HOST="16.171.237.146"
export EC2_USER="ec2-user"  # or "ubuntu" for Ubuntu
export EC2_KEY="~/.ssh/your-key.pem"
chmod +x aws/ec2/deploy-ec2.sh
./aws/ec2/deploy-ec2.sh
```

```powershell
# Windows PowerShell
$env:EC2_HOST = "16.171.237.146"
$env:EC2_USER = "ec2-user"
$env:EC2_KEY = "$HOME\.ssh\your-key.pem"
.\aws\ec2\deploy-ec2.ps1
```

See [aws/ec2/EC2_DEPLOYMENT.md](aws/ec2/EC2_DEPLOYMENT.md) for details.

### Option 2: Deploy with ECS Fargate (Scalable)

For production with auto-scaling and load balancing:

## Prerequisites

1. AWS CLI installed and configured
2. Docker installed and running
3. Environment variables set

## One-Command Deployment (Linux/Mac)

```bash
# Set variables
export ENVIRONMENT=production
export AWS_REGION=us-east-1
export DB_PASSWORD="your-secure-password-here"
export DB_USERNAME="admin"

# Deploy
chmod +x aws/*.sh && ./aws/deploy.sh
```

## One-Command Deployment (Windows)

```powershell
# Set variables
$env:ENVIRONMENT = "production"
$env:AWS_REGION = "us-east-1"
$env:DB_PASSWORD = "your-secure-password-here"
$env:DB_USERNAME = "admin"

# Deploy
.\aws\deploy.ps1
```

## Post-Deployment Steps

### 1. Update Secrets in AWS Secrets Manager

After deployment, update the secrets with actual values:

```bash
# Get secrets ARN
SECRETS_ARN=$(aws cloudformation describe-stacks \
    --stack-name missing-roles-agent-production-infrastructure \
    --query "Stacks[0].Outputs[?OutputKey=='SecretsManagerArn'].OutputValue" \
    --output text)

# Update secrets
aws secretsmanager update-secret \
    --secret-id "${SECRETS_ARN}" \
    --secret-string '{
        "SECRET_KEY": "your-django-secret-key",
        "DB_HOST": "missing-roles-agent-production-db.xxxxx.rds.amazonaws.com",
        "DB_USER": "admin",
        "DB_PASSWORD": "your-db-password",
        "OPENAI_API_KEY": "sk-your-openai-key",
        "ANTHROPIC_API_KEY": "sk-ant-your-key",
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4"
    }'
```

### 2. Run Database Migrations

```bash
# Linux/Mac
./aws/run-migrations.sh

# Windows
.\aws\run-migrations.ps1
```

### 3. Deploy Frontend

```bash
# Linux/Mac
./aws/deploy-frontend.sh

# Windows
.\aws\deploy-frontend.ps1
```

## Get Your URLs

```bash
# Get ALB endpoint (Backend API)
aws cloudformation describe-stacks \
    --stack-name missing-roles-agent-production-infrastructure \
    --query "Stacks[0].Outputs[?OutputKey=='ALBEndpoint'].OutputValue" \
    --output text

# Get CloudFront URL (Frontend)
aws cloudformation describe-stacks \
    --stack-name missing-roles-agent-production-infrastructure \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
    --output text
```

## That's It! 🎉

Your application is now deployed to AWS. Access it at:
- **Backend API**: `http://<alb-endpoint>`
- **Frontend**: `https://<cloudfront-url>`

## Troubleshooting

If something goes wrong:

1. Check CloudFormation stack events:
   ```bash
   aws cloudformation describe-stack-events \
       --stack-name missing-roles-agent-production-infrastructure
   ```

2. Check ECS service status:
   ```bash
   aws ecs describe-services \
       --cluster missing-roles-agent-production-cluster \
       --services missing-roles-agent-backend-service
   ```

3. View logs:
   ```bash
   aws logs tail /ecs/missing-roles-agent-production --follow
   ```

For more details, see [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md).

