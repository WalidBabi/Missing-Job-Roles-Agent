# EC2 Deployment Script for Windows PowerShell
# Deploys directly to an EC2 instance

$ErrorActionPreference = "Stop"

# Configuration
$EC2_HOST = if ($env:EC2_HOST) { $env:EC2_HOST } else { "16.171.237.146" }
$EC2_USER = if ($env:EC2_USER) { $env:EC2_USER } else { "ec2-user" }
$EC2_KEY = if ($env:EC2_KEY) { $env:EC2_KEY } else { "$HOME\.ssh\id_rsa" }
$PROJECT_NAME = "missing-roles-agent"
$APP_DIR = "/opt/${PROJECT_NAME}"

Write-Host "Deploying to EC2 Instance: ${EC2_HOST}" -ForegroundColor Green

# Check if SSH is available (requires OpenSSH or WSL)
Write-Host "`n[1/6] Checking SSH access..." -ForegroundColor Green
$sshTest = ssh -i "${EC2_KEY}" -o ConnectTimeout=5 "${EC2_USER}@${EC2_HOST}" "echo 'SSH connection successful'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Cannot connect to EC2 instance. Please check:" -ForegroundColor Red
    Write-Host "  - SSH key path: ${EC2_KEY}"
    Write-Host "  - EC2 user: ${EC2_USER}"
    Write-Host "  - Security group allows SSH (port 22)"
    Write-Host "`nNote: Windows requires OpenSSH or WSL for SSH access" -ForegroundColor Yellow
    exit 1
}

# Install dependencies on EC2
Write-Host "`n[2/6] Installing dependencies on EC2..." -ForegroundColor Green
$installScript = @"
    sudo yum update -y 2>/dev/null || sudo apt-get update -y
    if ! command -v python3.11 &> /dev/null; then
        sudo yum install -y python3.11 python3.11-pip python3.11-devel 2>/dev/null || \
        sudo apt-get install -y python3.11 python3.11-pip python3.11-dev
    fi
    sudo yum install -y mysql mysql-devel gcc 2>/dev/null || \
    sudo apt-get install -y default-mysql-client libmysqlclient-dev build-essential
    if ! command -v nginx &> /dev/null; then
        sudo yum install -y nginx 2>/dev/null || sudo apt-get install -y nginx
        sudo systemctl enable nginx
        sudo systemctl start nginx
    fi
"@

ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" $installScript

# Create application directory
Write-Host "`n[3/6] Setting up application directory..." -ForegroundColor Green
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "sudo mkdir -p ${APP_DIR}; sudo chown -R ${EC2_USER}:${EC2_USER} ${APP_DIR}"

# Copy application files (requires rsync or scp)
Write-Host "`n[4/6] Copying application files..." -ForegroundColor Green
Write-Host "Note: This requires rsync (available in WSL or Git Bash)" -ForegroundColor Yellow
Write-Host "Alternatively, you can use scp or manually copy files" -ForegroundColor Yellow

# For Windows, we'll use scp to copy key files
$filesToCopy = @("requirements-prod.txt", "requirements.txt", "manage.py", "Dockerfile", ".dockerignore")
foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        scp -i "${EC2_KEY}" $file "${EC2_USER}@${EC2_HOST}:${APP_DIR}/"
    }
}

# Copy directories
$dirsToCopy = @("missing_roles_project", "roles_analyzer", "frontend")
foreach ($dir in $dirsToCopy) {
    if (Test-Path $dir) {
        Write-Host "Copying ${dir}..." -ForegroundColor Yellow
        # Use tar for efficient copying
        tar czf - $dir 2>$null | ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "cd ${APP_DIR} && tar xzf -"
    }
}

# Setup Python environment
Write-Host "`n[5/6] Setting up Python environment..." -ForegroundColor Green
$setupScript = @"
cd ${APP_DIR}
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt
if [ ! -f .env ]; then
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=CHANGE_ME_IN_PRODUCTION
ALLOWED_HOSTS=16.171.237.146,localhost,127.0.0.1
DB_ENGINE=django.db.backends.mysql
DB_NAME=hr_database
DB_USER=admin
DB_PASSWORD=CHANGE_ME
DB_HOST=localhost
DB_PORT=3306
OPENAI_API_KEY=CHANGE_ME
ANTHROPIC_API_KEY=CHANGE_ME
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
CORS_ALLOWED_ORIGINS=http://16.171.237.146,http://localhost:3000
EOF
fi
"@

ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" $setupScript

# Setup nginx
Write-Host "`n[6/6] Configuring nginx..." -ForegroundColor Green
$nginxConfig = @"
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name 16.171.237.146;
    client_max_body_size 10M;
    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
    location /static/ {
        alias /opt/missing-roles-agent/staticfiles/;
        expires 30d;
    }
    location / {
        root /opt/missing-roles-agent/frontend/dist;
        try_files `$uri `$uri/ /index.html;
    }
}
"@

ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "echo '$nginxConfig' | sudo tee /etc/nginx/conf.d/missing-roles-agent.conf > /dev/null"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "sudo nginx -t && sudo systemctl reload nginx"

# Create systemd service
Write-Host "`n[7/7] Creating systemd service..." -ForegroundColor Green
$serviceConfig = @"
[Unit]
Description=Missing Job Roles Agent Django Application
After=network.target mysql.service

[Service]
Type=notify
User=${EC2_USER}
Group=${EC2_USER}
WorkingDirectory=${APP_DIR}
Environment=`"PATH=${APP_DIR}/venv/bin`"
ExecStart=${APP_DIR}/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile - missing_roles_project.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"@

ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "echo '$serviceConfig' | sudo tee /etc/systemd/system/missing-roles-agent.service > /dev/null"
ssh -i "${EC2_KEY}" "${EC2_USER}@${EC2_HOST}" "sudo systemctl daemon-reload && sudo systemctl enable missing-roles-agent.service"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. SSH: ssh -i ${EC2_KEY} ${EC2_USER}@${EC2_HOST}"
Write-Host "2. Update .env: cd ${APP_DIR} && nano .env"
Write-Host "3. Setup MySQL and run migrations"
Write-Host "4. Start service: sudo systemctl start missing-roles-agent"
Write-Host "`nApplication: http://${EC2_HOST}" -ForegroundColor Green

