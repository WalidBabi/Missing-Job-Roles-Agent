#!/bin/bash

echo "=== EC2 Instance Security Group Check ==="
echo ""

# Get instance metadata
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null)

if [ -z "$INSTANCE_ID" ]; then
    echo "Could not retrieve instance metadata. Are you running on EC2?"
    exit 1
fi

echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Region: $REGION"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Installing..."
    sudo yum install -y aws-cli
fi

echo "=== Current Security Groups attached to this instance ==="
aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].SecurityGroups[*].[GroupId,GroupName]' --output table

echo ""
echo "=== Checking inbound rules for port 5173 ==="
SECURITY_GROUPS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --region $REGION --query 'Reservations[0].Instances[0].SecurityGroups[*].GroupId' --output text)

for SG in $SECURITY_GROUPS; do
    echo "Security Group: $SG"
    aws ec2 describe-security-groups --group-ids $SG --region $REGION --query 'SecurityGroups[0].IpPermissions[?FromPort==`5173`]' --output table
    echo ""
done

echo "=== Checking inbound rules for port 8080 ==="
for SG in $SECURITY_GROUPS; do
    echo "Security Group: $SG"
    aws ec2 describe-security-groups --group-ids $SG --region $REGION --query 'SecurityGroups[0].IpPermissions[?FromPort==`8080`]' --output table
    echo ""
done

echo "=== Checking inbound rules for port 8000 ==="
for SG in $SECURITY_GROUPS; do
    echo "Security Group: $SG"
    aws ec2 describe-security-groups --group-ids $SG --region $REGION --query 'SecurityGroups[0].IpPermissions[?FromPort==`8000`]' --output table
    echo ""
done

echo ""
echo "=== Testing local connectivity ==="
echo "Testing localhost:5173..."
curl -s -I http://localhost:5173 | head -1

echo ""
echo "=== Recommendation ==="
echo "If port 5173 is not showing in the security group rules above,"
echo "you need to add it using the AWS Console or CLI:"
echo ""
echo "aws ec2 authorize-security-group-ingress \\"
echo "    --group-id <YOUR-SECURITY-GROUP-ID> \\"
echo "    --protocol tcp \\"
echo "    --port 5173 \\"
echo "    --cidr 0.0.0.0/0 \\"
echo "    --region $REGION"

