# Fix phpMyAdmin Access - Connection Timeout

## Problem
You're getting `ERR_CONNECTION_TIMED_OUT` when trying to access phpMyAdmin at `http://13.62.225.238:8080`.

## Root Cause
The AWS Security Group is blocking port 8080. The containers are running fine, but the security group needs to allow inbound traffic on port 8080.

## Solution

### Option 1: Use the Script (if AWS CLI is configured)

```bash
cd /home/ec2-user/Missing-Job-Roles-Agent
./add-port-8080.sh
```

Or with your specific IP:
```bash
./add-port-8080.sh YOUR_IP_ADDRESS/32
```

### Option 2: Manual Fix via AWS Console (Recommended)

1. **Go to AWS EC2 Console**
   - Open: https://console.aws.amazon.com/ec2/v2/home#SecurityGroups:
   - Or navigate: EC2 → Security Groups

2. **Find Your Security Group**
   - Search for: `sg-0e8009371e396dc81`
   - Or look for security group: `launch-wizard-6`

3. **Edit Inbound Rules**
   - Select the security group
   - Click **"Edit inbound rules"** button
   - Click **"Add rule"**

4. **Configure the Rule**
   - **Type**: Custom TCP
   - **Port range**: `8080`
   - **Source**: 
     - For testing: `0.0.0.0/0` (allows all IPs - less secure)
     - For production: Your IP address (e.g., `123.45.67.89/32` - more secure)
   - **Description** (optional): "phpMyAdmin access"

5. **Save**
   - Click **"Save rules"**

6. **Test**
   - Try accessing: http://13.62.225.238:8080
   - It should work immediately after saving

## Security Group Details

- **Security Group ID**: `sg-0e8009371e396dc81`
- **Security Group Name**: `launch-wizard-6`
- **Instance ID**: `i-01cd4a334e4c9e837`
- **Instance IP**: `13.62.225.238`

## Verify Containers Are Running

```bash
docker ps | grep phpmyadmin
```

You should see:
```
missing_roles_phpmyadmin   Up   ...   0.0.0.0:8080->80/tcp
```

## phpMyAdmin Login

Once you can access the page:
- **Server**: `db` (or leave default)
- **Username**: `root`
- **Password**: (empty - as configured)

## Security Best Practices

1. **Restrict Access**: Instead of `0.0.0.0/0`, use your specific IP address
   - Format: `YOUR_IP/32` (e.g., `203.0.113.45/32`)

2. **Use SSH Tunnel** (Most Secure):
   ```bash
   ssh -L 8080:localhost:8080 ec2-user@13.62.225.238
   ```
   Then access: http://localhost:8080

3. **Remove Rule When Done**: If you only need temporary access, remove the rule after use.

## Troubleshooting

### Still Can't Access?

1. **Check containers are running**:
   ```bash
   docker ps
   ```

2. **Check port is listening**:
   ```bash
   netstat -tlnp | grep 8080
   ```

3. **Check security group rules**:
   - Verify the rule was saved in AWS Console
   - Check the source IP matches your current IP

4. **Try restarting containers**:
   ```bash
   cd /home/ec2-user/Missing-Job-Roles-Agent
   docker-compose restart phpmyadmin
   ```

