#!/bin/bash

# CCTV Analytics - Database Migration and Setup Script

set -e

echo "🔧 Setting up CCTV Analytics Platform..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

echo "📦 Building Docker images..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🔄 Running migrations..."
docker compose exec -T backend python manage.py migrate

echo "📂 Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput

echo "👤 Creating superuser..."
docker compose exec -T backend python manage.py createsuperuser --noinput \
    --username=admin \
    --email=admin@example.com || echo "Superuser may already exist"

echo "📋 Creating subscription plans..."
docker compose exec -T backend python manage.py shell << EOF
from apps.subscriptions.models import SubscriptionPlan

plans = [
    {
        'name': 'Trial',
        'slug': 'trial',
        'price_monthly': 0,
        'price_annual': 0,
        'max_cameras': 5,
        'max_users': 3,
        'features': ['Basic analytics', 'Email alerts', 'Dashboard']
    },
    {
        'name': 'Starter',
        'slug': 'starter',
        'price_monthly': 99,
        'price_annual': 990,
        'max_cameras': 20,
        'max_users': 10,
        'features': ['Advanced analytics', 'Custom rules', 'Webhooks', 'API access']
    },
    {
        'name': 'Professional',
        'slug': 'professional',
        'price_monthly': 299,
        'price_annual': 2990,
        'max_cameras': 100,
        'max_users': 50,
        'features': ['All Starter features', 'Priority support', 'Dedicated storage', 'Custom branding']
    },
    {
        'name': 'Enterprise',
        'slug': 'enterprise',
        'price_monthly': 999,
        'price_annual': 9990,
        'max_cameras': 1000,
        'max_users': 500,
        'features': ['All Professional features', 'SLA', 'On-premise option', 'Custom integrations']
    }
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        slug=plan_data['slug'],
        defaults=plan_data
    )
    if created:
        print(f"✓ Created plan: {plan.name}")
    else:
        print(f"✓ Plan exists: {plan.name}")
EOF

echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "  - Frontend: http://localhost:5173"
echo "  - API: http://localhost:8000/api/v1"
echo "  - Admin: http://localhost:8000/admin"
echo ""
echo "📖 Default credentials (change in production):"
echo "  - Username: admin"
echo "  - Email: admin@example.com"
echo "  - Password: (set during setup)"
echo ""
echo "📚 Next steps:"
echo "  1. Create an organization at http://localhost:5173/setup"
echo "  2. Add a camera in the dashboard"
echo "  3. Test the camera connection"
echo "  4. Set up alerts and rules"
