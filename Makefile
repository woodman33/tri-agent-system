.PHONY: help build up down restart logs shell clean test

# Default target
help:
	@echo "Tri-Agent System - Docker Commands"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make restart  - Restart all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make shell    - Access shell in tri-agent container"
	@echo "  make clean    - Remove containers, volumes, and images"
	@echo "  make test     - Run tests in container"
	@echo ""

# Build Docker images
build:
	docker compose build

# Start all services
up:
	docker compose up -d

# Stop all services
down:
	docker compose down

# Restart all services
restart:
	docker compose restart

# View logs
logs:
	docker compose logs -f

# Access shell in tri-agent container
shell:
	docker compose exec tri-agent bash

# Remove everything
clean:
	docker compose down -v --rmi all

# Run tests
test:
	docker compose exec tri-agent python -m pytest

# Development mode (with logs)
dev:
	docker compose up
