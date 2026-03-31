#!/bin/bash

# Start the application with Docker Compose

if [ ! -f .env ]; then
    echo "❌ .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
    exit 1
fi

echo "🚀 Starting CCTV Analytics Platform..."
docker compose up -d

echo "✅ Services starting. Waiting for health checks..."
sleep 5

# Check health
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🌐 Access the application:"
echo "  - Frontend: http://localhost:5173"
echo "  - API: http://localhost:8000/api/v1"
echo "  - Admin: http://localhost:8000/admin"
