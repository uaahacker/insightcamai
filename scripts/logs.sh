#!/bin/bash

# View logs from all services or specific service

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "📋 Showing logs from all services..."
    docker compose logs -f --tail=100
else
    echo "📋 Showing logs from $SERVICE..."
    docker compose logs -f --tail=100 $SERVICE
fi
