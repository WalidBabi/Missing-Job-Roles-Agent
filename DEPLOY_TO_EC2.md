# Deploy to EC2 Instance (16.171.237.146)

Quick guide to deploy the Missing Job Roles AI Agent to your EC2 instance.

## Prerequisites

1. **SSH Access** to the EC2 instance
   - Your IP must be allowed in the security group (port 22)
   - You have the SSH private key (.pem file)

2. **Windows Requirements**:
   - OpenSSH client (usually pre-installed on Windows 10/11)
   - Or use WSL (Windows Subsystem for Linux)
   - Or use Git Bash

## Quick Deployment

### Option 1: Use the Quick Deploy Script (Recommended)

```powershell
# Run from project root
.\deploy-to-ec2.ps1
```

This script will:
- Test SSH connection
- Deploy the application
- Set up nginx
- Create systemd service

**Note**: You may need to update the SSH key path in `deploy-to-ec2.ps1` if your key is in a different location.

### Option 2: Manual Deployment

```powershell
# Set environment variables
$env:EC2_HOST = "16.171.237.146"
$env:EC2_USER = "ec2-user"  # or "ubuntu" for Ubuntu instances
$env:EC2_KEY = "$HOME\.ssh\id_rsa"  # or path to your .pem file

# Run deployment
.\aws\ec2\deploy-ec2.ps1
```

## After Deployment

### 1. SSH into the Instance

```powershell
ssh -i $HOME\.ssh\id_rsa ec2-user@16.171.237.146
```

Or if using a .pem file:
```powershell
ssh -i $HOME\.ssh\your-key.pem ec2-user@16.171.237.146
```

### 2. Update Environment Variables

```bash
cd /opt/missing-roles-agent
nano .env
```

Update these critical values:
- `SECRET_KEY` - Generate a new one (see below)
- `DB_PASSWORD` - Your MySQL password
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key (optional)

**Generate SECRET_KEY:**
```bash
cd /opt/missing-roles-agent
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Install and Setup MySQL

```bash
# Install MySQL (Amazon Linux)
sudo yum install -y mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Or for Ubuntu
sudo apt-get update
sudo apt-get install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# Secure MySQL installation
sudo mysql_secure_installation

# Create database
mysql -u root -p
```

In MySQL prompt:
```sql
CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON hr_database.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Update `.env` with the database password you just set.

### 4. Run Django Migrations

```bash
cd /opt/missing-roles-agent
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### 5. Start the Service

```bash
# Start the Django service
sudo systemctl start missing-roles-agent

# Enable auto-start on boot
sudo systemctl enable missing-roles-agent

# Check status
sudo systemctl status missing-roles-agent

# View logs
sudo journalctl -u missing-roles-agent -f
```

### 6. Verify Deployment

Open in your browser:
- **API**: http://16.171.237.146/api/job-roles/statistics/
- **Admin**: http://16.171.237.146/admin/

## Troubleshooting

### Cannot Connect via SSH

1. Check security group allows SSH (port 22) from your IP
2. Verify SSH key path is correct
3. Try: `ssh -v -i your-key.pem ec2-user@16.171.237.146` for verbose output

### Service Won't Start

```bash
# Check service status
sudo systemctl status missing-roles-agent

# Check logs
sudo journalctl -u missing-roles-agent -n 50

# Check if port 8000 is in use
sudo netstat -tulpn | grep 8000
```

### Database Connection Error

```bash
# Test MySQL connection
mysql -u admin -p hr_database

# Check MySQL is running
sudo systemctl status mysqld  # or mysql

# Verify .env has correct DB credentials
cat /opt/missing-roles-agent/.env | grep DB_
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

### Permission Errors

```bash
# Fix ownership
sudo chown -R ec2-user:ec2-user /opt/missing-roles-agent

# Fix execute permissions
chmod +x /opt/missing-roles-agent/venv/bin/gunicorn
```

## Security Checklist

- [ ] Changed `SECRET_KEY` in `.env`
- [ ] Changed default database password
- [ ] Security group only allows necessary ports
- [ ] Firewall configured (if applicable)
- [ ] Regular security updates: `sudo yum update` or `sudo apt-get update`

## Next Steps

1. **Set up HTTPS**: Use Let's Encrypt for SSL certificate
2. **Domain Name**: Point a domain to the EC2 IP
3. **Backups**: Set up automated database backups
4. **Monitoring**: Configure CloudWatch or similar
5. **Deploy Frontend**: Build and deploy React frontend

## Useful Commands

```bash
# Restart service
sudo systemctl restart missing-roles-agent

# View real-time logs
sudo journalctl -u missing-roles-agent -f

# Check nginx access logs
sudo tail -f /var/log/nginx/access.log

# Update application code
cd /opt/missing-roles-agent
git pull  # or copy new files
source venv/bin/activate
pip install -r requirements-prod.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart missing-roles-agent
```

## Support

For detailed documentation, see:
- [aws/ec2/EC2_DEPLOYMENT.md](aws/ec2/EC2_DEPLOYMENT.md) - Complete EC2 deployment guide
- [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - General AWS deployment guide

