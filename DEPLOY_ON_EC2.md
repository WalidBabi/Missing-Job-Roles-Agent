# Deploy on EC2 Instance (You're Already There!)

Since you're already SSH'd into the EC2 instance, here's how to deploy directly:

## Option 1: Quick Setup Script (Recommended)

If you're in the project directory on the EC2 instance:

```bash
# Make the script executable
chmod +x aws/ec2/quick-deploy.sh

# Run it
./aws/ec2/quick-deploy.sh
```

## Option 2: Manual Setup

### Step 1: Install Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3.11 python3.11-pip python3.11-devel

# Install MySQL dependencies
sudo yum install -y mysql mysql-devel gcc

# Install nginx
sudo yum install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 2: Setup Application Directory

```bash
# Create directory
sudo mkdir -p /opt/missing-roles-agent
sudo chown -R $USER:$USER /opt/missing-roles-agent

# Copy files (if you're in the project directory)
cp -r . /opt/missing-roles-agent/
# Or use rsync if available
# rsync -av --exclude 'venv' --exclude '__pycache__' ./ /opt/missing-roles-agent/
```

### Step 3: Setup Python Environment

```bash
cd /opt/missing-roles-agent

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-prod.txt
```

### Step 4: Create .env File

```bash
cd /opt/missing-roles-agent
nano .env
```

Add this content (update with your values):

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=16.171.237.146,localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=hr_database
DB_USER=admin
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306

# AI Provider
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-key
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# CORS
CORS_ALLOWED_ORIGINS=http://16.171.237.146,http://localhost:3000
```

**Generate SECRET_KEY:**
```bash
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 5: Setup MySQL

```bash
# Install MySQL server
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Secure MySQL (set root password)
sudo mysql_secure_installation

# Create database
mysql -u root -p
```

In MySQL:
```sql
CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON hr_database.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 6: Run Migrations

```bash
cd /opt/missing-roles-agent
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 7: Configure nginx

```bash
sudo nano /etc/nginx/conf.d/missing-roles-agent.conf
```

Add this configuration:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name 16.171.237.146 _;

    client_max_body_size 10M;

    location /api/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/missing-roles-agent/staticfiles/;
        expires 30d;
    }

    location / {
        root /opt/missing-roles-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

Test and reload nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: Create Systemd Service

```bash
sudo nano /etc/systemd/system/missing-roles-agent.service
```

Add this:

```ini
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
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable missing-roles-agent.service
sudo systemctl start missing-roles-agent.service
```

### Step 9: Check Status

```bash
# Check service status
sudo systemctl status missing-roles-agent

# View logs
sudo journalctl -u missing-roles-agent -f
```

## Verify Deployment

Open in your browser:
- **API**: http://16.171.237.146/api/job-roles/statistics/
- **Admin**: http://16.171.237.146/admin/

## Troubleshooting

### Service won't start
```bash
sudo journalctl -u missing-roles-agent -n 50
```

### Check if port 8000 is in use
```bash
sudo netstat -tulpn | grep 8000
```

### Test nginx
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Check database connection
```bash
mysql -u admin -p hr_database
```

## Quick Commands

```bash
# Restart service
sudo systemctl restart missing-roles-agent

# View logs
sudo journalctl -u missing-roles-agent -f

# Check status
sudo systemctl status missing-roles-agent
```

