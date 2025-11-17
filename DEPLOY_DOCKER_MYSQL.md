# Deploy with Docker MySQL and phpMyAdmin

This guide shows how to set up MySQL and phpMyAdmin using Docker on your EC2 instance.

## Quick Setup

### Step 1: Run the Setup Script

On your EC2 instance:

```bash
# Make script executable
chmod +x aws/ec2/setup-docker-mysql.sh

# Run it
./aws/ec2/setup-docker-mysql.sh
```

This will:
- Install Docker and Docker Compose (if not installed)
- Create docker-compose configuration
- Start MySQL and phpMyAdmin containers
- Set up the database

### Step 2: Update Passwords

```bash
# Edit the Docker environment file
nano /opt/missing-roles-agent/docker/.env
```

Update with secure passwords:
```env
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_PASSWORD=your_secure_password
```

Then restart containers:
```bash
cd /opt/missing-roles-agent/docker
docker compose down
docker compose up -d
```

### Step 3: Update Django .env File

```bash
cd /opt/missing-roles-agent
nano .env
```

Update database settings:
```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hr_database
DB_USER=admin
DB_PASSWORD=your_secure_password  # Same as MYSQL_PASSWORD in docker/.env
```

### Step 4: Test Database Connection

```bash
cd /opt/missing-roles-agent
source venv/bin/activate

# Test connection
python manage.py dbshell
```

If it connects, you're good! Exit with `exit`.

### Step 5: Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Access phpMyAdmin

Open in your browser:
- **phpMyAdmin**: http://16.171.237.146:8080

Login credentials:
- **Server**: `mysql`
- **Username**: `admin`
- **Password**: (the `MYSQL_PASSWORD` from docker/.env)

## Docker Commands

### View Container Status

```bash
cd /opt/missing-roles-agent/docker
docker compose ps
```

### View Logs

```bash
# All containers
docker compose logs -f

# Just MySQL
docker compose logs -f mysql

# Just phpMyAdmin
docker compose logs -f phpmyadmin
```

### Stop Containers

```bash
cd /opt/missing-roles-agent/docker
docker compose down
```

### Start Containers

```bash
cd /opt/missing-roles-agent/docker
docker compose up -d
```

### Restart Containers

```bash
cd /opt/missing-roles-agent/docker
docker compose restart
```

### Backup Database

```bash
cd /opt/missing-roles-agent/docker
docker compose exec mysql mysqldump -u admin -p hr_database > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
cd /opt/missing-roles-agent/docker
docker compose exec -T mysql mysql -u admin -p hr_database < backup_file.sql
```

## Security Group Configuration

Make sure your EC2 security group allows:
- **Port 8080** (phpMyAdmin) - from your IP only (recommended)
- **Port 3306** (MySQL) - only from localhost (default, no change needed)

To allow phpMyAdmin access:
1. Go to EC2 Console → Security Groups
2. Select your instance's security group
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 8080
   - Source: Your IP address (or 0.0.0.0/0 for testing, but not recommended)

## Troubleshooting

### Containers Won't Start

```bash
# Check Docker status
sudo systemctl status docker

# Check logs
cd /opt/missing-roles-agent/docker
docker compose logs
```

### Can't Connect to phpMyAdmin

1. Check security group allows port 8080
2. Check containers are running:
   ```bash
   docker ps
   ```
3. Check phpMyAdmin logs:
   ```bash
   docker compose logs phpmyadmin
   ```

### Django Can't Connect to MySQL

1. Verify MySQL container is running:
   ```bash
   docker ps | grep mysql
   ```
2. Test connection from Django:
   ```bash
   cd /opt/missing-roles-agent
   source venv/bin/activate
   python manage.py dbshell
   ```
3. Check DB_HOST in .env is `localhost` (not `mysql`)
4. Verify password matches docker/.env

### Port Already in Use

If port 3306 or 8080 is already in use:

```bash
# Find what's using the port
sudo netstat -tulpn | grep 3306
sudo netstat -tulpn | grep 8080

# Stop the conflicting service or change port in docker-compose.yml
```

## Configuration Summary

### Docker Configuration
- **Location**: `/opt/missing-roles-agent/docker/docker-compose.yml`
- **Environment**: `/opt/missing-roles-agent/docker/.env`

### Django Configuration
- **Location**: `/opt/missing-roles-agent/.env`
- **DB_HOST**: `localhost` (important! Not `mysql`)
- **DB_PORT**: `3306`
- **DB_NAME**: `hr_database`
- **DB_USER**: `admin`
- **DB_PASSWORD**: (same as MYSQL_PASSWORD in docker/.env)

### phpMyAdmin Access
- **URL**: http://16.171.237.146:8080
- **Server**: `mysql`
- **Username**: `admin`
- **Password**: (same as MYSQL_PASSWORD in docker/.env)

## Why DB_HOST=localhost?

Even though the MySQL container is named `mysql`, Django runs on the host machine (not in Docker), so it connects to MySQL through the exposed port 3306 on `localhost`. The container name `mysql` is only used by phpMyAdmin container (which is also in Docker) to connect to the MySQL container.

## Next Steps

1. ✅ MySQL and phpMyAdmin running
2. ✅ Django .env configured
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Start Django service: `sudo systemctl start missing-roles-agent`
5. ✅ Access phpMyAdmin: http://16.171.237.146:8080
6. ✅ Access Django API: http://16.171.237.146/api/

