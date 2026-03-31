#!/bin/bash

# Run migrations

echo "🔄 Running migrations..."
docker compose exec -T backend python manage.py migrate

echo "✅ Migrations complete"
