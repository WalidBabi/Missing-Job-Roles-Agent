#!/bin/bash

# Quick Deployment Script for EC2 Instance
# Run this script ON the EC2 instance after copying files

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_NAME="missing-roles-agent"
APP_DIR="/opt/${PROJECT_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Missing Job Roles Agent - Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "Please don't run as root. The script will use sudo when needed."
    exit 1
fi

# Update system
echo -e "${GREEN}[1/7] Updating system packages...${NC}"
sudo yum update -y 2>/dev/null || sudo apt-get update -y

# Install Python 3.11
echo -e "${GREEN}[2/7] Installing Python 3.11...${NC}"
if ! command -v python3.11 &> /dev/null; then
    sudo yum install -y python3.11 python3.11-pip python3.11-devel 2>/dev/null || \
    sudo apt-get install -y python3.11 python3.11-pip python3.11-dev
fi

# Install MySQL client and development libraries
echo -e "${GREEN}[3/7] Installing MySQL dependencies...${NC}"
sudo yum install -y mysql mysql-devel gcc 2>/dev/null || \
sudo apt-get install -y default-mysql-client libmysqlclient-dev build-essential

# Install nginx
echo -e "${GREEN}[4/7] Installing nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    sudo yum install -y nginx 2>/dev/null || sudo apt-get install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
fi

# Create application directory
echo -e "${GREEN}[5/7] Setting up application directory...${NC}"
if [ ! -d "${APP_DIR}" ]; then
    sudo mkdir -p "${APP_DIR}"
    sudo chown -R $USER:$USER "${APP_DIR}"
fi

# If we're in the project directory, copy files
if [ -f "manage.py" ]; then
    echo -e "${YELLOW}Copying files to ${APP_DIR}...${NC}"
    rsync -av --exclude 'venv' --exclude '__pycache__' --exclude '*.pyc' \
        --exclude '.git' --exclude 'node_modules' --exclude 'frontend/dist' \
        ./ "${APP_DIR}/" || cp -r . "${APP_DIR}/"
fi

# Setup Python virtual environment
echo -e "${GREEN}[6/7] Setting up Python environment...${NC}"
cd "${APP_DIR}"

if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt 2>/dev/null || pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=CHANGE_ME_IN_PRODUCTION
ALLOWED_HOSTS=16.171.237.146,localhost,127.0.0.1

# Database
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
    echo -e "${YELLOW}.env file created. Please update with your actual values.${NC}"
fi

# Setup nginx configuration
echo -e "${GREEN}[7/7] Configuring nginx...${NC}"
sudo tee /etc/nginx/conf.d/missing-roles-agent.conf > /dev/null << 'NGINXCONF'
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name 16.171.237.146 _;

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

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

# Create systemd service
echo -e "${GREEN}Creating systemd service...${NC}"
sudo tee /etc/systemd/system/missing-roles-agent.service > /dev/null << SERVICECONF
[Unit]
Description=Missing Job Roles Agent Django Application
After=network.target mysql.service

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn \
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

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update .env file:"
echo "   cd ${APP_DIR}"
echo "   nano .env"
echo ""
echo "2. Install and setup MySQL:"
echo "   sudo yum install -y mysql-server"
echo "   sudo systemctl start mysqld"
echo "   mysql -u root -p"
echo "   CREATE DATABASE hr_database;"
echo ""
echo "3. Run migrations:"
echo "   cd ${APP_DIR}"
echo "   source venv/bin/activate"
echo "   python manage.py migrate"
echo "   python manage.py collectstatic --noinput"
echo ""
echo "4. Start the service:"
echo "   sudo systemctl start missing-roles-agent"
echo ""
echo "5. Check status:"
echo "   sudo systemctl status missing-roles-agent"
echo ""
echo -e "${GREEN}Application will be available at: http://16.171.237.146${NC}"

