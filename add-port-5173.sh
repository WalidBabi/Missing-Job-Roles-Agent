#!/bin/bash

echo "=== Adding Port 5173 to Security Group ==="
echo ""

# Get instance metadata using IMDSv2
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "Error: Could not get IMDSv2 token. Are you running on EC2?"
    exit 1
fi

INSTANCE_ID=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
REGION=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)
PUBLIC_IP=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)

echo "Instance ID: $INSTANCE_ID"
echo "Region: $REGION"
echo "Public IP: $PUBLIC_IP"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI is not configured with credentials."
    echo ""
    echo "Please configure AWS CLI with:"
    echo "  aws configure"
    echo ""
    echo "Or attach an IAM role to this EC2 instance with EC2 permissions."
    echo ""
    echo "Alternatively, use the AWS Console to add the security group rule manually."
    echo "See FIX_PORT_5173_ACCESS.md for detailed instructions."
    exit 1
fi

# Get the security group ID
SECURITY_GROUP_ID=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text)

if [ -z "$SECURITY_GROUP_ID" ]; then
    echo "Error: Could not get security group ID"
    exit 1
fi

echo "Security Group ID: $SECURITY_GROUP_ID"
echo ""

# Check if rule already exists
EXISTING_RULE=$(aws ec2 describe-security-groups \
    --group-ids $SECURITY_GROUP_ID \
    --region $REGION \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`5173\` && ToPort==\`5173\`]" \
    --output text)

if [ ! -z "$EXISTING_RULE" ]; then
    echo "✅ Port 5173 rule already exists in security group $SECURITY_GROUP_ID"
    echo ""
    echo "Rule details:"
    aws ec2 describe-security-groups \
        --group-ids $SECURITY_GROUP_ID \
        --region $REGION \
        --query "SecurityGroups[0].IpPermissions[?FromPort==\`5173\`]" \
        --output table
else
    echo "Adding port 5173 to security group $SECURITY_GROUP_ID..."
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 5173 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully added port 5173 to security group!"
    else
        echo "❌ Failed to add port 5173. Check your AWS permissions."
        exit 1
    fi
fi

echo ""
echo "=== Testing connectivity ==="
echo "Testing local access..."
if curl -s -I http://localhost:5173 | grep -q "200 OK"; then
    echo "✅ Local access works (http://localhost:5173)"
else
    echo "⚠️  Local access test failed"
fi

echo ""
echo "Your application should now be accessible at:"
echo "  http://$PUBLIC_IP:5173"
echo ""
echo "Test it with:"
echo "  curl http://$PUBLIC_IP:5173"
echo ""
echo "Or open in your browser:"
echo "  http://$PUBLIC_IP:5173"

