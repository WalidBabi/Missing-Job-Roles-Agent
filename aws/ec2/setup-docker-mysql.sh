#!/bin/bash

# Setup MySQL and phpMyAdmin with Docker
# Run this script on the EC2 instance

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setting up MySQL and phpMyAdmin with Docker${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    sudo yum install -y docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. You may need to log out and back in for group changes.${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    # Also create symlink for docker compose (v2)
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
fi

# Create directory for docker-compose
DOCKER_DIR="/opt/missing-roles-agent/docker"
mkdir -p "${DOCKER_DIR}"

# Copy docker-compose file
if [ -f "aws/ec2/docker-compose.mysql.yml" ]; then
    cp aws/ec2/docker-compose.mysql.yml "${DOCKER_DIR}/docker-compose.yml"
elif [ -f "docker-compose.mysql.yml" ]; then
    cp docker-compose.mysql.yml "${DOCKER_DIR}/docker-compose.yml"
else
    echo -e "${RED}docker-compose.mysql.yml not found. Creating default...${NC}"
    cat > "${DOCKER_DIR}/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: missing-roles-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-changeme}
      MYSQL_DATABASE: hr_database
      MYSQL_USER: admin
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-changeme}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD:-changeme}"]
      interval: 10s
      timeout: 5s
      retries: 5

  phpmyadmin:
    image: phpmyadmin/phpmyadmin
    container_name: missing-roles-phpmyadmin
    restart: always
    environment:
      PMA_HOST: mysql
      PMA_PORT: 3306
      PMA_USER: admin
      PMA_PASSWORD: ${MYSQL_PASSWORD:-changeme}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-changeme}
    ports:
      - "8080:80"
    depends_on:
      mysql:
        condition: service_healthy
    links:
      - mysql

volumes:
  mysql_data:
EOF
fi

# Create .env file for docker-compose
if [ ! -f "${DOCKER_DIR}/.env" ]; then
    echo -e "${YELLOW}Creating .env file for Docker...${NC}"
    cat > "${DOCKER_DIR}/.env" << 'EOF'
MYSQL_ROOT_PASSWORD=changeme_root_password
MYSQL_PASSWORD=changeme_password
EOF
    echo -e "${YELLOW}Please update ${DOCKER_DIR}/.env with your actual passwords${NC}"
fi

# Start Docker containers
echo -e "${GREEN}Starting MySQL and phpMyAdmin containers...${NC}"
cd "${DOCKER_DIR}"

# Use docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for MySQL to be ready
echo -e "${YELLOW}Waiting for MySQL to be ready...${NC}"
sleep 10

# Check container status
echo -e "${GREEN}Container status:${NC}"
docker ps | grep -E "missing-roles-mysql|missing-roles-phpmyadmin"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}MySQL Configuration:${NC}"
echo "  Host: localhost (or 127.0.0.1)"
echo "  Port: 3306"
echo "  Database: hr_database"
echo "  User: admin"
echo "  Password: (check ${DOCKER_DIR}/.env)"
echo ""
echo -e "${YELLOW}phpMyAdmin:${NC}"
echo "  URL: http://16.171.237.146:8080"
echo "  Server: mysql"
echo "  Username: admin"
echo "  Password: (check ${DOCKER_DIR}/.env)"
echo ""
echo -e "${YELLOW}Update your Django .env file:${NC}"
echo "  DB_HOST=localhost"
echo "  DB_PORT=3306"
echo "  DB_NAME=hr_database"
echo "  DB_USER=admin"
echo "  DB_PASSWORD=(from ${DOCKER_DIR}/.env)"
echo ""
echo -e "${GREEN}To view logs:${NC}"
echo "  cd ${DOCKER_DIR}"
echo "  docker compose logs -f"
echo ""
echo -e "${GREEN}To stop containers:${NC}"
echo "  cd ${DOCKER_DIR}"
echo "  docker compose down"
echo ""
echo -e "${GREEN}To restart containers:${NC}"
echo "  cd ${DOCKER_DIR}"
echo "  docker compose restart"

