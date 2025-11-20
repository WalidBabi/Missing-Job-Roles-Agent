#!/bin/bash

# Script to add port 8080 to AWS Security Group for phpMyAdmin access

SECURITY_GROUP_NAME="launch-wizard-6"
PORT=8080

echo "=========================================="
echo "Adding port $PORT to Security Group: $SECURITY_GROUP_NAME"
echo "=========================================="

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [ -z "$SG_ID" ] || [ "$SG_ID" == "None" ]; then
    echo "ERROR: Could not find security group '$SECURITY_GROUP_NAME'"
    echo ""
    echo "Please add the rule manually:"
    echo "1. Go to AWS EC2 Console: https://console.aws.amazon.com/ec2/"
    echo "2. Click 'Security Groups' in the left menu"
    echo "3. Find and select security group: $SECURITY_GROUP_NAME"
    echo "4. Click 'Edit inbound rules'"
    echo "5. Click 'Add rule'"
    echo "6. Configure:"
    echo "   - Type: Custom TCP"
    echo "   - Port: $PORT"
    echo "   - Source: 0.0.0.0/0 (or your specific IP for better security)"
    echo "7. Click 'Save rules'"
    exit 1
fi

echo "Found Security Group ID: $SG_ID"
echo ""

# Check if rule already exists
EXISTING=$(aws ec2 describe-security-groups \
    --group-ids $SG_ID \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`$PORT\` && ToPort==\`$PORT\`]" \
    --output text 2>/dev/null)

if [ ! -z "$EXISTING" ]; then
    echo "Rule for port $PORT already exists!"
    echo ""
    echo "Current rules for port $PORT:"
    aws ec2 describe-security-groups \
        --group-ids $SG_ID \
        --query "SecurityGroups[0].IpPermissions[?FromPort==\`$PORT\` && ToPort==\`$PORT\`].[FromPort,ToPort,IpProtocol,IpRanges[0].CidrIp]" \
        --output table
    exit 0
fi

# Add the rule
echo "Adding inbound rule for port $PORT..."
echo ""

# Ask for source IP (default to 0.0.0.0/0 for testing)
read -p "Enter source IP (default: 0.0.0.0/0 for all IPs, or enter your IP): " SOURCE_IP
SOURCE_IP=${SOURCE_IP:-0.0.0.0/0}

echo ""
echo "Adding rule: Port $PORT from $SOURCE_IP"
echo ""

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port $PORT \
    --cidr $SOURCE_IP 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Port $PORT has been added to security group."
    echo ""
    echo "You should now be able to access phpMyAdmin at:"
    echo "http://13.62.225.238:8080"
    echo ""
    echo "Note: If you used 0.0.0.0/0, consider restricting to your IP for better security."
else
    echo ""
    echo "❌ Failed to add rule. You may need to add it manually via AWS Console."
    echo ""
    echo "Manual steps:"
    echo "1. Go to: https://console.aws.amazon.com/ec2/v2/home?region=$(aws configure get region 2>/dev/null || echo 'us-east-1')#SecurityGroups:"
    echo "2. Select security group: $SECURITY_GROUP_NAME"
    echo "3. Click 'Edit inbound rules' → 'Add rule'"
    echo "4. Type: Custom TCP, Port: $PORT, Source: $SOURCE_IP"
fi

