# Docker Setup Documentation

## Overview

This document provides detailed information about the Docker setup for the tri-agent-system.

## Files Included

### Dockerfile
- **Base Image**: Python 3.11 slim
- **Working Directory**: `/app`
- **Exposed Port**: 8000
- **Features**:
  - Multi-stage build support
  - System dependencies: build-essential, curl, git
  - Conditional Python requirements installation
  - Optimized layer caching
  
### docker-compose.yml
A complete multi-service setup including:

1. **tri-agent** (Main Application)
   - Builds from local Dockerfile
   - Port mapping: 8000:8000
   - Volume mounting for hot-reload development
   - Connected to tri-agent-network

2. **redis** (Message Queue/Cache)
   - Image: redis:7-alpine
   - Port mapping: 6379:6379
   - Persistent storage with volume
   - AOF (Append-Only File) enabled

3. **postgres** (Database)
   - Image: postgres:15-alpine
   - Port mapping: 5432:5432
   - Persistent storage with volume
   - Pre-configured with default credentials

### .dockerignore
Excludes unnecessary files from the Docker build context:
- Git files and directories
- Python cache and virtual environments
- IDE configuration files
- Testing artifacts
- Distribution packages
- Log files
- Environment files
- Documentation build artifacts

### .env.example
Template for environment variables:
- Database configuration (PostgreSQL)
- Redis configuration
- Application settings
- API keys placeholder

## Build Commands

### Build the Docker Image
```bash
docker build -t tri-agent-system .
```

### Build with specific tag
```bash
docker build -t tri-agent-system:v1.0.0 .
```

### Build without cache
```bash
docker build --no-cache -t tri-agent-system .
```

## Run Commands

### Using Docker Compose (Recommended)

Start all services:
```bash
docker compose up
```

Start in detached mode:
```bash
docker compose up -d
```

View logs:
```bash
docker compose logs -f
```

Stop services:
```bash
docker compose down
```

Stop and remove volumes:
```bash
docker compose down -v
```

### Using Docker Directly

Run the container:
```bash
docker run -p 8000:8000 tri-agent-system
```

Run in detached mode:
```bash
docker run -d -p 8000:8000 --name tri-agent tri-agent-system
```

Run with environment variables:
```bash
docker run -p 8000:8000 -e PORT=8000 -e ENVIRONMENT=production tri-agent-system
```

## Development Workflow

### Hot Reload Development
The docker-compose setup includes volume mounting for development:

1. Start services: `docker compose up`
2. Edit files locally
3. Changes are reflected in the container automatically

### Accessing Container Shell
```bash
docker compose exec tri-agent bash
```

### Running Commands in Container
```bash
docker compose exec tri-agent python manage.py migrate
```

### Viewing Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f tri-agent

# With timestamp
docker compose logs -f -t tri-agent
```

## Network Configuration

The setup creates a bridge network called `tri-agent-network` that allows:
- Inter-service communication
- Service discovery by service name
- Isolated network environment

Services can communicate using their service names:
- `redis:6379`
- `postgres:5432`

## Volume Management

### List volumes
```bash
docker volume ls
```

### Inspect volume
```bash
docker volume inspect tri-agent-system_postgres-data
docker volume inspect tri-agent-system_redis-data
```

### Backup volume
```bash
docker run --rm -v tri-agent-system_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

### Restore volume
```bash
docker run --rm -v tri-agent-system_postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

## Troubleshooting

### Container won't start
Check logs:
```bash
docker compose logs tri-agent
```

### Port already in use
Change the port mapping in docker-compose.yml or stop the conflicting service:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Permission issues
Ensure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
```

### Out of disk space
Clean up unused Docker resources:
```bash
# Remove unused containers, networks, images
docker system prune

# Remove volumes too
docker system prune -a --volumes
```

### Cannot connect to database
1. Ensure postgres service is running: `docker compose ps`
2. Check postgres logs: `docker compose logs postgres`
3. Verify connection string uses service name: `postgres:5432`

## Production Considerations

1. **Use specific versions**: Replace `latest` tags with specific versions
2. **Secure credentials**: Use Docker secrets or external secret management
3. **Health checks**: Add health check configurations
4. **Resource limits**: Set memory and CPU limits
5. **Logging**: Configure proper log drivers
6. **Monitoring**: Add monitoring solutions (Prometheus, Grafana)
7. **Backup strategy**: Implement automated backup solutions
8. **Network security**: Use custom networks and firewall rules
9. **Image scanning**: Scan images for vulnerabilities
10. **Multi-stage builds**: Optimize image size with multi-stage builds

## Best Practices

1. **Keep images small**: Use Alpine base images when possible
2. **Layer caching**: Order Dockerfile commands for optimal caching
3. **No secrets in images**: Never include secrets in Dockerfiles
4. **Use .dockerignore**: Minimize build context size
5. **Named volumes**: Use named volumes for important data
6. **Health checks**: Implement health check endpoints
7. **Graceful shutdown**: Handle SIGTERM signals properly
8. **One process per container**: Follow single-responsibility principle
9. **Read-only filesystems**: Use read-only root filesystem when possible
10. **Non-root user**: Run containers as non-root user

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)
