#!/bin/bash

# Create Django superuser

echo "👤 Creating superuser..."
docker compose exec backend python manage.py createsuperuser --interactive
