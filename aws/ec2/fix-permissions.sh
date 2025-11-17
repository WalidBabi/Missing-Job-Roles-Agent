#!/bin/bash

# Fix permissions for the project directory
# Run this script to fix ownership issues

echo "Fixing permissions..."

# Fix current directory ownership
sudo chown -R $USER:$USER .

# Create and fix /opt/missing-roles-agent if needed
sudo mkdir -p /opt/missing-roles-agent
sudo chown -R $USER:$USER /opt/missing-roles-agent

echo "Permissions fixed!"
echo "Current directory is now owned by: $(whoami)"
ls -la . | head -5

