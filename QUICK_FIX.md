# Quick Fix for Permission Issues

## Problem
The directory is owned by root instead of ec2-user.

## Solution

Run these commands on your EC2 instance:

```bash
# Fix current directory ownership
sudo chown -R $USER:$USER .

# Create and fix /opt directory
sudo mkdir -p /opt/missing-roles-agent
sudo chown -R $USER:$USER /opt/missing-roles-agent

# Or use the fix script
chmod +x aws/ec2/fix-permissions.sh
./aws/ec2/fix-permissions.sh
```

## Then Continue with Docker Setup

After fixing permissions:

```bash
# Make sure Docker group is active (if you just added yourself)
newgrp docker

# Or log out and back in
exit
# Then SSH back in

# Continue with Docker setup
./aws/ec2/setup-docker-mysql.sh
```

## Alternative: Run Setup Script Again

The updated script should handle permissions automatically now. Just run:

```bash
./aws/ec2/setup-docker-mysql.sh
```

