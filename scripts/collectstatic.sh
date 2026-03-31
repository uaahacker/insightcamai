#!/bin/bash

# Collect static files

echo "📂 Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput

echo "✅ Static files collected"
