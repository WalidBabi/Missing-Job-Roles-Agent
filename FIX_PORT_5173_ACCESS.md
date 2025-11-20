# Fix Port 5173 Access Issue

## Current Status
✅ **Vite server is running** on port 5173 and listening on all interfaces (0.0.0.0)
✅ **Node.js upgraded** to version 20.19.5
✅ **No local firewall** blocking the port
❌ **Cannot access from public IP** (13.62.225.238:5173)

## Instance Details
- **Instance ID**: i-01cd4a334e4c9e837
- **Region**: eu-north-1
- **Public IP**: 13.62.225.238

## Problem
The security group rules are visible in your screenshot, but the connection is still timing out. This suggests one of these issues:

### Issue 1: Security Group Not Attached to Instance
The security groups in your screenshot might not be attached to this specific EC2 instance.

**Solution**: In AWS Console:
1. Go to EC2 → Instances
2. Select instance `i-01cd4a334e4c9e837`
3. Click **Actions** → **Security** → **Change Security Groups**
4. Make sure the security group with port 5173 rule is checked/attached
5. Click **Save**

### Issue 2: Wrong Source IP in Security Group Rule
The security group rule might be restricting access to specific IPs instead of 0.0.0.0/0

**Solution**: In AWS Console:
1. Go to EC2 → Security Groups
2. Find the security group attached to your instance
3. Check the **Inbound rules** tab
4. For port 5173, make sure the **Source** is set to `0.0.0.0/0` (or your specific IP)
5. If not, edit the rule and change it

### Issue 3: Network ACL Blocking Traffic
VPC Network ACLs might be blocking the traffic even if security groups allow it.

**Solution**: In AWS Console:
1. Go to VPC → Network ACLs
2. Find the Network ACL for your subnet
3. Check **Inbound Rules**
4. Make sure there's a rule allowing TCP port 5173 from 0.0.0.0/0
5. If not, add a rule:
   - Rule #: 100 (or next available)
   - Type: Custom TCP
   - Port: 5173
   - Source: 0.0.0.0/0
   - Allow/Deny: ALLOW

### Issue 4: VPC Route Table Issues
Less common, but routing might be misconfigured.

**Solution**: In AWS Console:
1. Go to VPC → Route Tables
2. Find the route table for your subnet
3. Make sure there's a route: `0.0.0.0/0` → `igw-xxxxx` (Internet Gateway)

## Quick Fix: Add Security Group Rule via AWS CLI

If you have AWS CLI configured with proper permissions, run:

```bash
# Get your security group ID
aws ec2 describe-instances \
    --instance-ids i-01cd4a334e4c9e837 \
    --region eu-north-1 \
    --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
    --output text

# Add the rule (replace <SECURITY-GROUP-ID> with the output from above)
aws ec2 authorize-security-group-ingress \
    --group-id <SECURITY-GROUP-ID> \
    --protocol tcp \
    --port 5173 \
    --cidr 0.0.0.0/0 \
    --region eu-north-1
```

## Verify the Fix

After making changes, test with:

```bash
# From your local machine (not the EC2 instance)
curl http://13.62.225.238:5173
```

Or open in browser:
```
http://13.62.225.238:5173
```

## Current Server Status

The Vite dev server is running with:
- **Node.js**: v20.19.5
- **Port**: 5173
- **Binding**: 0.0.0.0 (all interfaces)
- **Process ID**: Check with `lsof -ti:5173`

To restart the server if needed:
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9

# Start server
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20
cd /home/ec2-user/Missing-Job-Roles-Agent/frontend
npm run dev
```

## Most Likely Solution

Based on the screenshot showing multiple security group rules, the most likely issue is that **the security group with the port 5173 rule is not attached to your EC2 instance**. 

**Action Required**:
1. Go to AWS Console → EC2 → Instances
2. Select your instance (i-01cd4a334e4c9e837)
3. Look at the **Security** tab at the bottom
4. Check which security groups are attached
5. If the security group with port 5173 (sgr-070b1a2e75ac62d92) is not listed:
   - Click **Actions** → **Security** → **Change Security Groups**
   - Add the security group that has the port 5173 rule
   - Click **Save**

After attaching the correct security group, the site should be accessible immediately at:
**http://13.62.225.238:5173**

