.PHONY: help up down build logs shell-backend shell-frontend migrate seed test clean

help:
	@echo "SO-101 Setup Builder"
	@echo ""
	@echo "Usage:"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make build       - Build all containers"
	@echo "  make logs        - View logs"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed database with initial data"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove containers and volumes"

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker-compose exec backend python -m scripts.seed_db

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f
