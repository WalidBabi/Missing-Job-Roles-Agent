# Quick Deployment Script for EC2 Instance
# This script deploys to your EC2 instance at 16.171.237.146

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Missing Job Roles Agent - EC2 Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$EC2_HOST = "16.171.237.146"
$EC2_USER = "ec2-user"  # Change to "ubuntu" if using Ubuntu instance
$EC2_KEY = "$HOME\.ssh\id_rsa"  # Change to your SSH key path

Write-Host "Target: ${EC2_USER}@${EC2_HOST}" -ForegroundColor Yellow
Write-Host "SSH Key: ${EC2_KEY}" -ForegroundColor Yellow
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $EC2_KEY)) {
    Write-Host "ERROR: SSH key not found at ${EC2_KEY}" -ForegroundColor Red
    Write-Host "Please update EC2_KEY variable in this script with your SSH key path" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common locations:" -ForegroundColor Yellow
    Write-Host "  - $HOME\.ssh\id_rsa" -ForegroundColor Gray
    Write-Host "  - $HOME\.ssh\your-key.pem" -ForegroundColor Gray
    exit 1
}

# Check SSH connection
Write-Host "[1/7] Testing SSH connection..." -ForegroundColor Green
try {
    $testResult = ssh -i "${EC2_KEY}" -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${EC2_USER}@${EC2_HOST}" "echo 'Connected'" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ SSH connection successful" -ForegroundColor Green
    } else {
        throw "Connection failed"
    }
} catch {
    Write-Host "✗ Cannot connect to EC2 instance" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "  1. EC2 instance is running" -ForegroundColor Gray
    Write-Host "  2. Security group allows SSH (port 22) from your IP" -ForegroundColor Gray
    Write-Host "  3. SSH key path is correct: ${EC2_KEY}" -ForegroundColor Gray
    Write-Host "  4. EC2 user is correct (ec2-user for Amazon Linux, ubuntu for Ubuntu)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Note: Windows requires OpenSSH client or WSL for SSH access" -ForegroundColor Yellow
    exit 1
}

# Set environment variables for the deployment script
$env:EC2_HOST = $EC2_HOST
$env:EC2_USER = $EC2_USER
$env:EC2_KEY = $EC2_KEY

Write-Host ""
Write-Host "[2/7] Running deployment script..." -ForegroundColor Green
Write-Host ""

# Run the deployment script
& ".\aws\ec2\deploy-ec2.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Initiated Successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. SSH into the instance:" -ForegroundColor White
    Write-Host "   ssh -i ${EC2_KEY} ${EC2_USER}@${EC2_HOST}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Update environment variables:" -ForegroundColor White
    Write-Host "   cd /opt/missing-roles-agent" -ForegroundColor Gray
    Write-Host "   nano .env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Setup MySQL database:" -ForegroundColor White
    Write-Host "   sudo yum install -y mysql-server" -ForegroundColor Gray
    Write-Host "   sudo systemctl start mysqld" -ForegroundColor Gray
    Write-Host "   mysql -u root -p" -ForegroundColor Gray
    Write-Host "   CREATE DATABASE hr_database;" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Run migrations:" -ForegroundColor White
    Write-Host "   source venv/bin/activate" -ForegroundColor Gray
    Write-Host "   python manage.py migrate" -ForegroundColor Gray
    Write-Host "   python manage.py collectstatic --noinput" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Start the service:" -ForegroundColor White
    Write-Host "   sudo systemctl start missing-roles-agent" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Application will be available at:" -ForegroundColor Cyan
    Write-Host "   http://${EC2_HOST}" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "Deployment encountered errors. Please check the output above." -ForegroundColor Red
}

