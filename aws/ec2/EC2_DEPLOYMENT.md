# EC2 Direct Deployment Guide

This guide explains how to deploy the Missing Job Roles AI Agent directly to an EC2 instance.

## Prerequisites

1. **EC2 Instance** running Amazon Linux 2 or Ubuntu
2. **SSH Access** to the instance
3. **SSH Key** for authentication
4. **Security Group** configured to allow:
   - SSH (port 22) from your IP
   - HTTP (port 80) from anywhere
   - HTTPS (port 443) from anywhere (optional)

## Quick Deployment

### For Linux/Mac:

```bash
# Set EC2 configuration
export EC2_HOST="16.171.237.146"
export EC2_USER="ec2-user"  # or "ubuntu" for Ubuntu instances
export EC2_KEY="~/.ssh/your-key.pem"

# Make script executable
chmod +x aws/ec2/deploy-ec2.sh

# Deploy
./aws/ec2/deploy-ec2.sh
```

### For Windows (PowerShell):

```powershell
# Set EC2 configuration
$env:EC2_HOST = "16.171.237.146"
$env:EC2_USER = "ec2-user"  # or "ubuntu" for Ubuntu instances
$env:EC2_KEY = "$HOME\.ssh\your-key.pem"

# Deploy (requires OpenSSH or WSL)
.\aws\ec2\deploy-ec2.ps1
```

## What the Script Does

1. **Checks SSH Access** - Verifies connection to EC2 instance
2. **Installs Dependencies** - Python 3.11, MySQL, nginx, Docker
3. **Creates App Directory** - `/opt/missing-roles-agent`
4. **Copies Application Files** - Transfers code to EC2
5. **Sets Up Python Environment** - Creates venv and installs dependencies
6. **Configures nginx** - Sets up reverse proxy
7. **Creates Systemd Service** - Auto-starts Django application

## Post-Deployment Steps

### 1. SSH into the Instance

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@16.171.237.146
```

### 2. Update Environment Variables

```bash
cd /opt/missing-roles-agent
nano .env
```

Update these values:
- `SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` - Your MySQL password
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key (optional)

### 3. Setup MySQL Database

```bash
# Install MySQL server (if not already installed)
sudo yum install -y mysql-server  # Amazon Linux
# or
sudo apt-get install -y mysql-server  # Ubuntu

# Start MySQL
sudo systemctl start mysqld  # Amazon Linux
sudo systemctl start mysql   # Ubuntu
sudo systemctl enable mysqld  # or mysql

# Secure MySQL installation
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

### 4. Run Django Migrations

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

### 5. Start the Service

```bash
# Start the Django service
sudo systemctl start missing-roles-agent

# Check status
sudo systemctl status missing-roles-agent

# View logs
sudo journalctl -u missing-roles-agent -f
```

### 6. Deploy Frontend (Optional)

```bash
cd /opt/missing-roles-agent/frontend

# Install Node.js (if not installed)
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs  # Amazon Linux
# or
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt-get install -y nodejs  # Ubuntu

# Build frontend
npm install
VITE_API_URL="http://16.171.237.146/api" npm run build
```

## Accessing the Application

- **Backend API**: `http://16.171.237.146/api/`
- **Django Admin**: `http://16.171.237.146/admin/`
- **Frontend**: `http://16.171.237.146/` (if deployed)

## Service Management

### Start/Stop/Restart Service

```bash
sudo systemctl start missing-roles-agent
sudo systemctl stop missing-roles-agent
sudo systemctl restart missing-roles-agent
sudo systemctl status missing-roles-agent
```

### View Logs

```bash
# Service logs
sudo journalctl -u missing-roles-agent -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Update Application

```bash
# Pull latest code (if using git)
cd /opt/missing-roles-agent
git pull  # or copy new files

# Update dependencies
source venv/bin/activate
pip install -r requirements-prod.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart missing-roles-agent
```

## Security Considerations

1. **Firewall**: Configure security groups to restrict access
2. **SSL/TLS**: Set up Let's Encrypt certificate for HTTPS
3. **Secrets**: Never commit `.env` file to version control
4. **Updates**: Keep system and dependencies updated
5. **Backups**: Regular database backups

### Enable HTTPS with Let's Encrypt

```bash
# Install certbot
sudo yum install -y certbot python3-certbot-nginx  # Amazon Linux
sudo apt-get install -y certbot python3-certbot-nginx  # Ubuntu

# Get certificate
sudo certbot --nginx -d 16.171.237.146

# Auto-renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status missing-roles-agent

# Check logs
sudo journalctl -u missing-roles-agent -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

### Database Connection Issues

```bash
# Test MySQL connection
mysql -u admin -p hr_database

# Check MySQL status
sudo systemctl status mysqld  # or mysql

# Check Django can connect
cd /opt/missing-roles-agent
source venv/bin/activate
python manage.py dbshell
```

### nginx Issues

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ec2-user:ec2-user /opt/missing-roles-agent

# Fix permissions
chmod +x /opt/missing-roles-agent/venv/bin/gunicorn
```

## Cost Optimization

- Use `t3.micro` or `t3.small` instance types
- Enable CloudWatch monitoring
- Set up auto-scaling if needed
- Use RDS for database (separate from EC2) for better performance

## Next Steps

1. Set up domain name and DNS
2. Configure SSL certificate
3. Set up automated backups
4. Configure CloudWatch monitoring
5. Set up CI/CD pipeline

