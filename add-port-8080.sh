#!/bin/bash

# Quick script to add port 8080 to the security group
# Security Group ID: sg-0e8009371e396dc81

SG_ID="sg-0e8009371e396dc81"
PORT=8080

echo "=========================================="
echo "Adding port $PORT to Security Group"
echo "Security Group ID: $SG_ID"
echo "=========================================="
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI is not configured."
    echo ""
    echo "Please configure AWS CLI first:"
    echo "  aws configure"
    echo ""
    echo "OR add the rule manually via AWS Console:"
    echo ""
    echo "1. Go to: https://console.aws.amazon.com/ec2/v2/home#SecurityGroups:"
    echo "2. Search for: $SG_ID"
    echo "3. Select it and click 'Edit inbound rules'"
    echo "4. Click 'Add rule'"
    echo "5. Configure:"
    echo "   - Type: Custom TCP"
    echo "   - Port range: $PORT"
    echo "   - Source: 0.0.0.0/0 (or your specific IP)"
    echo "6. Click 'Save rules'"
    exit 1
fi

# Check if rule already exists
echo "Checking existing rules..."
EXISTING=$(aws ec2 describe-security-groups \
    --group-ids $SG_ID \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`$PORT\` && ToPort==\`$PORT\` && IpProtocol==\`tcp\`]" \
    --output text 2>/dev/null)

if [ ! -z "$EXISTING" ]; then
    echo "✅ Rule for port $PORT already exists!"
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

# Default to 0.0.0.0/0 but allow override
SOURCE_IP="${1:-0.0.0.0/0}"

if [ "$SOURCE_IP" == "0.0.0.0/0" ]; then
    echo "⚠️  WARNING: Adding rule for ALL IPs (0.0.0.0/0)"
    echo "   For better security, consider restricting to your IP address."
    echo ""
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

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
    if [ "$SOURCE_IP" == "0.0.0.0/0" ]; then
        echo "⚠️  Security Note: Consider restricting this to your IP address later."
    fi
else
    echo ""
    echo "❌ Failed to add rule."
    echo ""
    echo "Possible reasons:"
    echo "  - Rule already exists"
    echo "  - Insufficient permissions"
    echo "  - AWS CLI not properly configured"
    echo ""
    echo "Please add the rule manually via AWS Console:"
    echo "https://console.aws.amazon.com/ec2/v2/home#SecurityGroups:search=$SG_ID"
fi

