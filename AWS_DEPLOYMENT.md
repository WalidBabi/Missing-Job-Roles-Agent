# AWS Production Deployment Guide

Complete guide for deploying the Missing Job Roles AI Agent to AWS.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Configuration](#configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

The application is deployed on AWS using the following architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    CloudFront CDN                            │
│              (Frontend Static Files)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Application Load Balancer                       │
│                    (Port 80/443)                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              ECS Fargate Cluster                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Task 1     │  │   Task 2     │  │   Task N     │     │
│  │  (Django)    │  │  (Django)    │  │  (Django)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              RDS MySQL (Private Subnet)                     │
│              Secrets Manager (API Keys)                     │
│              S3 (Frontend Static Files)                     │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **CloudFront**: CDN for frontend static files
2. **Application Load Balancer**: Routes traffic to ECS tasks
3. **ECS Fargate**: Containerized Django backend
4. **RDS MySQL**: Managed database
5. **S3**: Frontend static files storage
6. **Secrets Manager**: Secure storage for API keys and secrets
7. **VPC**: Isolated network with public/private subnets

---

## ✅ Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws --version
   aws configure
   ```
3. **Docker** installed and running
   ```bash
   docker --version
   ```
4. **Required Environment Variables**:
   - `DB_PASSWORD`: MySQL database password (min 8 characters)
   - `DB_USERNAME`: MySQL username (default: admin)
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: AI provider API key
   - `SECRET_KEY`: Django secret key (generate a secure one)

5. **AWS Permissions**: Your AWS user/role needs:
   - CloudFormation (create/update stacks)
   - ECS (create clusters, services, tasks)
   - ECR (create repositories, push images)
   - RDS (create databases)
   - VPC (create networking resources)
   - IAM (create roles and policies)
   - Secrets Manager (create/update secrets)
   - S3 (create buckets, upload files)
   - CloudFront (create distributions)

---

## 🚀 Quick Start

### 1. Set Environment Variables

```bash
export ENVIRONMENT=production
export AWS_REGION=us-east-1
export DB_PASSWORD="your-secure-password-here"
export DB_USERNAME="admin"
```

### 2. Deploy Infrastructure

```bash
# Make scripts executable
chmod +x aws/deploy.sh
chmod +x aws/deploy-frontend.sh
chmod +x aws/run-migrations.sh

# Deploy backend infrastructure
./aws/deploy.sh
```

### 3. Update Secrets

After infrastructure is created, update secrets in AWS Secrets Manager:

```bash
# Get secrets ARN from CloudFormation outputs
SECRETS_ARN=$(aws cloudformation describe-stacks \
    --stack-name missing-roles-agent-production-infrastructure \
    --query "Stacks[0].Outputs[?OutputKey=='SecretsManagerArn'].OutputValue" \
    --output text)

# Update secrets (replace with your actual values)
aws secretsmanager update-secret \
    --secret-id "${SECRETS_ARN}" \
    --secret-string '{
        "SECRET_KEY": "your-django-secret-key-here",
        "DB_HOST": "missing-roles-agent-production-db.xxxxx.us-east-1.rds.amazonaws.com",
        "DB_USER": "admin",
        "DB_PASSWORD": "your-db-password",
        "OPENAI_API_KEY": "sk-your-openai-key",
        "ANTHROPIC_API_KEY": "sk-ant-your-anthropic-key",
        "LLM_PROVIDER": "openai",
        "LLM_MODEL": "gpt-4"
    }'
```

### 4. Run Database Migrations

```bash
./aws/run-migrations.sh
```

### 5. Deploy Frontend

```bash
./aws/deploy-frontend.sh
```

---

## 📝 Step-by-Step Deployment

### Step 1: Review CloudFormation Template

The infrastructure is defined in `aws/cloudformation/infrastructure.yaml`. Review and customize if needed:

- VPC CIDR blocks
- Instance sizes
- Database configuration
- Region selection

### Step 2: Deploy Infrastructure

The deployment script will:

1. Create/update CloudFormation stack
2. Create VPC with public/private subnets
3. Create RDS MySQL instance
4. Create ECS cluster
5. Create Application Load Balancer
6. Create S3 bucket for frontend
7. Create CloudFront distribution
8. Set up security groups
9. Create IAM roles

```bash
./aws/deploy.sh
```

**Expected time**: 15-20 minutes

### Step 3: Build and Push Docker Image

The script automatically:
1. Creates ECR repository
2. Builds Docker image
3. Pushes to ECR

### Step 4: Configure Secrets

Update AWS Secrets Manager with your actual values:

**Required Secrets:**
- `SECRET_KEY`: Django secret key (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DB_HOST`: RDS endpoint (from CloudFormation outputs)
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `LLM_PROVIDER`: `openai` or `anthropic`
- `LLM_MODEL`: Model name (e.g., `gpt-4`, `claude-3-5-sonnet-20241022`)

### Step 5: Register ECS Task Definition

The script automatically registers the task definition with:
- Container image from ECR
- Environment variables
- Secrets from Secrets Manager
- Logging configuration
- Health checks

### Step 6: Create ECS Service

The service will:
- Run 2 tasks by default (configurable)
- Use Fargate launch type
- Connect to Application Load Balancer
- Auto-scale based on load

### Step 7: Run Database Migrations

```bash
./aws/run-migrations.sh
```

This creates a one-time ECS task to run Django migrations.

### Step 8: Deploy Frontend

```bash
./aws/deploy-frontend.sh
```

This will:
1. Build React frontend
2. Upload to S3
3. Invalidate CloudFront cache

---

## ⚙️ Configuration

### Environment Variables

Set these before running deployment:

```bash
export ENVIRONMENT=production          # or staging, development
export AWS_REGION=us-east-1           # Your preferred AWS region
export DB_PASSWORD="secure-password"   # MySQL password
export DB_USERNAME="admin"             # MySQL username
```

### CloudFormation Parameters

Edit `aws/cloudformation/infrastructure.yaml` to customize:

- `DatabaseInstanceClass`: RDS instance size (default: `db.t3.micro`)
- `ECSDesiredCount`: Number of ECS tasks (default: 2)
- `VpcCidr`: VPC CIDR block (default: `10.0.0.0/16`)

### ECS Task Definition

Edit `aws/ecs/task-definition.json` to customize:

- CPU/Memory allocation
- Container port
- Health check settings
- Logging configuration

### Frontend Configuration

The frontend automatically uses the ALB endpoint for API calls. The `VITE_API_URL` is set during build based on the ALB DNS name.

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Get log group name
LOG_GROUP="/ecs/missing-roles-agent-production"

# View logs
aws logs tail "${LOG_GROUP}" --follow --region us-east-1
```

### Check ECS Service Status

```bash
CLUSTER_NAME="missing-roles-agent-production-cluster"
SERVICE_NAME="missing-roles-agent-backend-service"

aws ecs describe-services \
    --cluster "${CLUSTER_NAME}" \
    --services "${SERVICE_NAME}" \
    --region us-east-1
```

### Check RDS Status

```bash
aws rds describe-db-instances \
    --db-instance-identifier missing-roles-agent-production-db \
    --region us-east-1
```

### Update Application

To deploy a new version:

```bash
# 1. Build and push new image
./aws/deploy.sh

# 2. ECS will automatically deploy new tasks (rolling update)
```

### Scale ECS Service

```bash
aws ecs update-service \
    --cluster missing-roles-agent-production-cluster \
    --service missing-roles-agent-backend-service \
    --desired-count 4 \
    --region us-east-1
```

### Database Backups

RDS automatically creates daily backups (retention: 7 days). To create a manual snapshot:

```bash
aws rds create-db-snapshot \
    --db-instance-identifier missing-roles-agent-production-db \
    --db-snapshot-identifier manual-snapshot-$(date +%Y%m%d) \
    --region us-east-1
```

---

## 🔧 Troubleshooting

### Issue: CloudFormation Stack Fails

**Check**: Stack events for specific error
```bash
aws cloudformation describe-stack-events \
    --stack-name missing-roles-agent-production-infrastructure \
    --region us-east-1
```

**Common causes**:
- Insufficient IAM permissions
- Resource limits (e.g., VPCs, RDS instances)
- Invalid parameter values

### Issue: ECS Tasks Not Starting

**Check**: Task definition and service status
```bash
aws ecs describe-tasks \
    --cluster missing-roles-agent-production-cluster \
    --tasks <task-id> \
    --region us-east-1
```

**Common causes**:
- Invalid secrets in Secrets Manager
- Network configuration issues
- Container health check failures

### Issue: Cannot Connect to Database

**Check**:
1. Security group allows traffic from ECS security group
2. RDS is in private subnet
3. Database credentials in Secrets Manager are correct

### Issue: Frontend Cannot Reach API

**Check**:
1. CORS settings in Django (update `CORS_ALLOWED_ORIGINS`)
2. ALB endpoint is correct
3. Security groups allow traffic

### Issue: High Costs

**Optimize**:
- Use `db.t3.micro` for RDS (free tier eligible)
- Use Fargate Spot for ECS (up to 70% savings)
- Use CloudFront caching
- Set up auto-scaling

---

## 🔒 Security Best Practices

1. **Secrets Management**: All sensitive data in AWS Secrets Manager
2. **Network Isolation**: Database in private subnet, no public access
3. **Security Groups**: Least privilege access
4. **SSL/TLS**: Enable HTTPS on ALB (requires ACM certificate)
5. **Database Encryption**: RDS encryption at rest enabled
6. **IAM Roles**: Use IAM roles, not access keys
7. **Regular Updates**: Keep Docker images and dependencies updated

### Enable HTTPS

1. Request ACM certificate:
```bash
aws acm request-certificate \
    --domain-name api.yourdomain.com \
    --validation-method DNS \
    --region us-east-1
```

2. Update ALB listener to use HTTPS (port 443)
3. Update CloudFormation template to include certificate

---

## 📈 Cost Estimation

**Monthly costs (approximate)**:

- RDS `db.t3.micro`: ~$15/month
- ECS Fargate (2 tasks, 1 vCPU, 2GB): ~$60/month
- Application Load Balancer: ~$20/month
- CloudFront: ~$5/month (first 10GB free)
- S3: ~$1/month
- Secrets Manager: ~$0.40/month
- Data Transfer: ~$10/month

**Total**: ~$110-150/month

**Cost Optimization**:
- Use Fargate Spot: Save 70% on compute
- Use smaller RDS instance for staging
- Enable CloudFront caching
- Use Reserved Instances for RDS (1-year commitment)

---

## 🎯 Next Steps

1. **Set up CI/CD**: Use GitHub Actions or AWS CodePipeline
2. **Enable Monitoring**: Set up CloudWatch alarms
3. **Add Auto-scaling**: Configure ECS auto-scaling based on CPU/memory
4. **Enable HTTPS**: Add SSL certificate to ALB
5. **Set up Backup Strategy**: Configure RDS automated backups
6. **Add Custom Domain**: Configure Route 53 for custom domain
7. **Enable Logging**: Set up centralized logging with CloudWatch Logs Insights

---

## 📞 Support

For issues or questions:
1. Check CloudFormation stack events
2. Review ECS task logs
3. Check RDS status
4. Verify security group rules
5. Review this documentation

---

## ✅ Deployment Checklist

- [ ] AWS CLI configured
- [ ] Docker installed and running
- [ ] Environment variables set
- [ ] CloudFormation stack deployed
- [ ] Secrets updated in Secrets Manager
- [ ] Docker image pushed to ECR
- [ ] ECS service created and running
- [ ] Database migrations completed
- [ ] Frontend deployed to S3/CloudFront
- [ ] Health checks passing
- [ ] API accessible via ALB
- [ ] Frontend accessible via CloudFront
- [ ] CORS configured correctly

---

**Deployment Complete!** 🎉

Your application should now be accessible at:
- **Backend API**: `http://<alb-endpoint>`
- **Frontend**: `https://<cloudfront-url>`

