#!/bin/bash
# Health check script for tri-agent-system Docker services

set -e

echo "==================================="
echo "Tri-Agent System Health Check"
echo "==================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local service=$1
    local port=$2
    
    if docker compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓${NC} $service is running"
        
        # Check if port is accessible
        if nc -z localhost $port 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Port $port is accessible"
        else
            echo -e "  ${YELLOW}⚠${NC} Port $port is not accessible"
        fi
    else
        echo -e "${RED}✗${NC} $service is not running"
        return 1
    fi
    echo ""
}

# Function to check Docker and Docker Compose
check_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker is installed"
        docker --version
    else
        echo -e "${RED}✗${NC} Docker is not installed"
        return 1
    fi
    
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker Compose is installed"
        docker compose version
    else
        echo -e "${RED}✗${NC} Docker Compose is not installed"
        return 1
    fi
    echo ""
}

# Check Docker installation
echo "Checking Docker installation..."
check_docker

# Check if services are running
echo "Checking services..."
check_service "tri-agent" "8000"
check_service "redis" "6379"
check_service "postgres" "5432"

# Check volumes
echo "Checking volumes..."
if docker volume ls | grep -q "tri-agent-system_postgres-data"; then
    echo -e "${GREEN}✓${NC} PostgreSQL volume exists"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL volume does not exist"
fi

if docker volume ls | grep -q "tri-agent-system_redis-data"; then
    echo -e "${GREEN}✓${NC} Redis volume exists"
else
    echo -e "${YELLOW}⚠${NC} Redis volume does not exist"
fi
echo ""

# Check network
echo "Checking network..."
if docker network ls | grep -q "tri-agent-system_tri-agent-network"; then
    echo -e "${GREEN}✓${NC} tri-agent-network exists"
else
    echo -e "${YELLOW}⚠${NC} tri-agent-network does not exist"
fi
echo ""

echo "==================================="
echo "Health check complete!"
echo "==================================="
