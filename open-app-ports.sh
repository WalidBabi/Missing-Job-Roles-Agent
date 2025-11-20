#!/bin/bash

# Script to open ports for the Missing Job Roles Application
# Security Group ID: sg-0e8009371e396dc81
# Public IP: 13.62.225.238

SG_ID="sg-0e8009371e396dc81"
PUBLIC_IP="13.62.225.238"

echo "=========================================="
echo "Opening Application Ports"
echo "Security Group ID: $SG_ID"
echo "Public IP: $PUBLIC_IP"
echo "=========================================="
echo ""

# Ports to open
declare -A PORTS=(
    [5173]="Frontend (React/Vite)"
    [8000]="Backend API (Django)"
    [8080]="phpMyAdmin"
)

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI is not configured."
    echo ""
    echo "Please configure AWS CLI first:"
    echo "  aws configure"
    echo ""
    echo "OR add the rules manually via AWS Console:"
    echo ""
    echo "Go to: https://console.aws.amazon.com/ec2/v2/home#SecurityGroups:search=$SG_ID"
    echo ""
    echo "Add these inbound rules:"
    for PORT in "${!PORTS[@]}"; do
        echo "  - Type: Custom TCP, Port: $PORT, Source: 0.0.0.0/0, Description: ${PORTS[$PORT]}"
    done
    echo ""
    exit 1
fi

# Function to add a port
add_port() {
    local PORT=$1
    local DESC=$2
    
    echo "----------------------------------------"
    echo "Port: $PORT - $DESC"
    echo "----------------------------------------"
    
    # Check if rule already exists
    EXISTING=$(aws ec2 describe-security-groups \
        --group-ids $SG_ID \
        --query "SecurityGroups[0].IpPermissions[?FromPort==\`$PORT\` && ToPort==\`$PORT\` && IpProtocol==\`tcp\`]" \
        --output text 2>/dev/null)
    
    if [ ! -z "$EXISTING" ]; then
        echo "✅ Port $PORT already open"
        return 0
    fi
    
    echo "Adding port $PORT..."
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port $PORT \
        --cidr 0.0.0.0/0 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Port $PORT opened successfully"
    else
        echo "❌ Failed to open port $PORT (may already exist)"
    fi
}

# Add all ports
for PORT in "${!PORTS[@]}"; do
    add_port $PORT "${PORTS[$PORT]}"
    echo ""
done

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "You can now access the application at:"
echo ""
echo "  🌐 Frontend:   http://$PUBLIC_IP:5173"
echo "  🔌 Backend:    http://$PUBLIC_IP:8000"
echo "  🗄️  phpMyAdmin: http://$PUBLIC_IP:8080"
echo ""
echo "API Documentation:"
echo "  http://$PUBLIC_IP:8000/api/"
echo ""
echo "⚠️  Note: These ports are open to the internet (0.0.0.0/0)"
echo "   For production, restrict to specific IP addresses."
echo ""




