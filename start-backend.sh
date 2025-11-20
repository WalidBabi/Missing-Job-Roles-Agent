#!/bin/bash

echo "=== Starting Django Backend Server ==="

# Get public IP using IMDSv2
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null)
PUBLIC_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)

# Kill any existing process on port 8000
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing existing process on port 8000..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# Navigate to project directory
cd /home/ec2-user/Missing-Job-Roles-Agent

# Activate virtual environment
source venv311/bin/activate

# Set environment variables
export ALLOWED_HOSTS="localhost,127.0.0.1,$PUBLIC_IP"
export CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,http://$PUBLIC_IP:5173,http://localhost:5173"

# Start the server
echo "Starting Django server..."
echo "Server will be available at:"
echo "  - Local: http://localhost:8000"
if [ ! -z "$PUBLIC_IP" ]; then
    echo "  - Public: http://$PUBLIC_IP:8000"
fi
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000

