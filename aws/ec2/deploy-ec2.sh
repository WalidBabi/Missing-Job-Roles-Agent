#!/bin/bash

# EC2 Deployment Script for Missing Job Roles Agent
# Deploys directly to an EC2 instance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
EC2_HOST="${EC2_HOST:-16.171.237.146}"
EC2_USER="${EC2_USER:-ec2-user}"
EC2_KEY="${EC2_KEY:-~/.ssh/id_rsa}"
PROJECT_NAME="missing-roles-agent"
APP_DIR="/opt/${PROJECT_NAME}"

echo -e "${GREEN}Deploying to EC2 Instance: ${EC2_HOST}${NC}"

# Check SSH access
echo -e "\n${GREEN}[1/6] Checking SSH access...${NC}"
if ! ssh -i "${EC2_KEY}" -o ConnectTimeout=5 "${EC2_USER}@${EC2_HOST}" "echo 'SSH connection successful'" 2>/dev/null; then
    echo -e "${RED}Cannot connect to EC2 instance. Please check:${NC}"
    echo -e "  - SSH key path: ${EC2_KEY}"
    echo -e "  - EC2 user: ${EC2_USER}"
    echo -e "  - Security group allows SSH (port 22)"
    exit 1
fi

# Install dependencies on EC2
echo -e "\n${GREEN}[2/6] Installing dependencies on EC2...${NC}"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" << 'ENDSSH'
    # Update system
    sudo yum update -y || sudo apt-get update -y
    
    # Install Python 3.11 and pip
    if ! command -v python3.11 &> /dev/null; then
        sudo yum install -y python3.11 python3.11-pip python3.11-devel || \
        sudo apt-get install -y python3.11 python3.11-pip python3.11-dev
    fi
    
    # Install MySQL client and development libraries
    sudo yum install -y mysql mysql-devel gcc || \
    sudo apt-get install -y default-mysql-client libmysqlclient-dev build-essential
    
    # Install nginx
    if ! command -v nginx &> /dev/null; then
        sudo yum install -y nginx || sudo apt-get install -y nginx
        sudo systemctl enable nginx
        sudo systemctl start nginx
    fi
    
    # Install Docker (optional, for containerized deployment)
    if ! command -v docker &> /dev/null; then
        sudo yum install -y docker || sudo apt-get install -y docker.io
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $USER
    fi
ENDSSH

# Create application directory
echo -e "\n${GREEN}[3/6] Setting up application directory...${NC}"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" << ENDSSH
    sudo mkdir -p ${APP_DIR}
    sudo chown -R ${EC2_USER}:${EC2_USER} ${APP_DIR}
ENDSSH

# Copy application files
echo -e "\n${GREEN}[4/6] Copying application files...${NC}"
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.git' --exclude 'node_modules' --exclude 'frontend/dist' \
    -e "ssh -i ${EC2_KEY}" \
    ./ "${EC2_USER}@${EC2_HOST}:${APP_DIR}/"

# Setup Python virtual environment and install dependencies
echo -e "\n${GREEN}[5/6] Setting up Python environment...${NC}"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" << 'ENDSSH'
    cd /opt/missing-roles-agent
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install production requirements
    pip install -r requirements-prod.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
DEBUG=False
SECRET_KEY=CHANGE_ME_IN_PRODUCTION
ALLOWED_HOSTS=16.171.237.146,localhost,127.0.0.1

# Database (update with your MySQL credentials)
DB_ENGINE=django.db.backends.mysql
DB_NAME=hr_database
DB_USER=admin
DB_PASSWORD=CHANGE_ME
DB_HOST=localhost
DB_PORT=3306

# AI Provider
OPENAI_API_KEY=CHANGE_ME
ANTHROPIC_API_KEY=CHANGE_ME
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# CORS
CORS_ALLOWED_ORIGINS=http://16.171.237.146,http://localhost:3000
EOF
        echo ".env file created. Please update with your actual values."
    fi
ENDSSH

# Setup nginx configuration
echo -e "\n${GREEN}[6/6] Configuring nginx...${NC}"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" << 'ENDSSH'
    sudo tee /etc/nginx/conf.d/missing-roles-agent.conf > /dev/null << 'NGINXCONF'
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name 16.171.237.146;

    client_max_body_size 10M;

    # Backend API
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /opt/missing-roles-agent/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Frontend (if deployed)
    location / {
        root /opt/missing-roles-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public";
    }
}
NGINXCONF

    # Test nginx configuration
    sudo nginx -t
    
    # Reload nginx
    sudo systemctl reload nginx
ENDSSH

# Create systemd service for Django
echo -e "\n${GREEN}[7/7] Creating systemd service...${NC}"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" << 'ENDSSH'
    sudo tee /etc/systemd/system/missing-roles-agent.service > /dev/null << 'SERVICECONF'
[Unit]
Description=Missing Job Roles Agent Django Application
After=network.target mysql.service

[Service]
Type=notify
User=ec2-user
Group=ec2-user
WorkingDirectory=/opt/missing-roles-agent
Environment="PATH=/opt/missing-roles-agent/venv/bin"
ExecStart=/opt/missing-roles-agent/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    missing_roles_project.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICECONF

    sudo systemctl daemon-reload
    sudo systemctl enable missing-roles-agent.service
ENDSSH

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. SSH into the instance: ssh -i ${EC2_KEY} ${EC2_USER}@${EC2_HOST}"
echo -e "2. Update .env file with your actual values:"
echo -e "   cd ${APP_DIR}"
echo -e "   nano .env"
echo -e "3. Setup MySQL database:"
echo -e "   mysql -u root -p"
echo -e "   CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo -e "4. Run migrations:"
echo -e "   source venv/bin/activate"
echo -e "   python manage.py migrate"
echo -e "   python manage.py collectstatic --noinput"
echo -e "5. Start the service:"
echo -e "   sudo systemctl start missing-roles-agent"
echo -e "6. Check status:"
echo -e "   sudo systemctl status missing-roles-agent"
echo -e "\n${GREEN}Application will be available at: http://${EC2_HOST}${NC}"

