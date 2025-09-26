.PHONY: help build up down logs clean install-backend install-frontend test

# Default target
help:
	@echo "Available commands:"
	@echo "  build           - Build all Docker images"
	@echo "  up              - Start all services"
	@echo "  down            - Stop all services"
	@echo "  logs            - Show logs from all services"
	@echo "  clean           - Clean up Docker resources"
	@echo "  install-backend - Install backend dependencies"
	@echo "  install-frontend- Install frontend dependencies"
	@echo "  test            - Run tests"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

# Development commands
install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

test:
	cd backend && pytest
	cd frontend && npm test

# Database commands
db-migrate:
	cd backend && alembic upgrade head

db-reset:
	docker-compose down postgres
	docker volume rm pair-trading-tool_postgres_data
	docker-compose up -d postgres
	sleep 5
	cd backend && alembic upgrade head
