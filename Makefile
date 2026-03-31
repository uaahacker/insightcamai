.PHONY: help up down logs migrate createsuperuser collectstatic shell test clean

help:
	@echo "CCTV Analytics Platform - Available Commands"
	@echo ""
	@echo "Setup & Management:"
	@echo "  make setup           - Initial setup (migrations, static files, superuser)"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make restart         - Restart all services"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         - Run Django migrations"
	@echo "  make createsuperuser - Create admin user"
	@echo "  make collectstatic   - Collect static files"
	@echo ""
	@echo "Utilities:"
	@echo "  make logs            - Show service logs"
	@echo "  make logs-backend    - Show backend logs only"
	@echo "  make logs-worker     - Show celery worker logs"
	@echo "  make shell           - Open Django shell"
	@echo "  make clean           - Remove containers and volumes"
	@echo "  make ps              - Show running containers"
	@echo ""
	@echo "Development:"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linting"

setup:
	@bash scripts/setup.sh

up:
	@bash scripts/start.sh

down:
	@bash scripts/stop.sh

restart: down up

logs:
	@docker compose logs -f --tail=100

logs-backend:
	@docker compose logs -f --tail=100 backend

logs-worker:
	@docker compose logs -f --tail=100 celery_worker

migrate:
	@docker compose exec -T backend python manage.py migrate

createsuperuser:
	@docker compose exec backend python manage.py createsuperuser

collectstatic:
	@docker compose exec -T backend python manage.py collectstatic --noinput

shell:
	@docker compose exec backend python manage.py shell

test:
	@docker compose exec -T backend python manage.py test

lint:
	@docker compose exec -T backend flake8 apps config --max-line-length=100

clean:
	@docker compose down -v
	@echo "✅ Removed all containers and volumes"

ps:
	@docker compose ps

.DEFAULT_GOAL := help
