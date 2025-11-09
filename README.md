# tri-agent-system

A multi-agent system for collaborative task processing.

## Docker Setup

This project includes Docker configuration for easy deployment and development.

### Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

### Quick Start

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

2. **Access the services:**
   - Main application: http://localhost:8000
   - Redis: localhost:6379
   - PostgreSQL: localhost:5432

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

4. **Stop and remove volumes:**
   ```bash
   docker-compose down -v
   ```

### Development

#### Building the Docker image

```bash
docker build -t tri-agent-system .
```

#### Running the container

```bash
docker run -p 8000:8000 tri-agent-system
```

#### View logs

```bash
docker-compose logs -f tri-agent
```

#### Accessing a service shell

```bash
docker-compose exec tri-agent bash
```

### Environment Variables

Configure the application using environment variables in a `.env` file:

```env
# Database configuration
POSTGRES_USER=triagent
POSTGRES_PASSWORD=triagent
POSTGRES_DB=triagent

# Redis configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Application settings
PORT=8000
```

### Service Architecture

The Docker Compose setup includes:

- **tri-agent**: Main application service
- **redis**: In-memory data store for agent communication
- **postgres**: PostgreSQL database for persistent storage

### Production Deployment

For production deployments, consider:

1. Using specific version tags instead of `latest`
2. Setting secure passwords via environment variables
3. Implementing proper volume backups
4. Using Docker secrets for sensitive data
5. Setting up health checks and monitoring

### Troubleshooting

#### Port already in use
If you get a "port already in use" error, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change host port
```

#### Permission issues
If you encounter permission issues, ensure your user is in the docker group:

```bash
sudo usermod -aG docker $USER
```

Then log out and log back in.