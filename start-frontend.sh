#!/bin/bash

echo "=== Starting Frontend Vite Server ==="

# Load NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Use Node 20
nvm use 20

# Get public IP using IMDSv2
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null)
PUBLIC_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)

# Kill any existing process on port 5173
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "Killing existing process on port 5173..."
    lsof -ti:5173 | xargs kill -9
    sleep 2
fi

# Navigate to frontend directory
cd /home/ec2-user/Missing-Job-Roles-Agent/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the server
echo "Starting Vite dev server..."
echo "Server will be available at:"
echo "  - Local: http://localhost:5173"
if [ ! -z "$PUBLIC_IP" ]; then
    echo "  - Public: http://$PUBLIC_IP:5173"
fi
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev

