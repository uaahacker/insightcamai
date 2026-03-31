# Testing Guide

Complete guide for testing the CCTV Analytics platform.

## Test Environment Setup

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-django pytest-asyncio coverage factory-boy faker

# For frontend
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

## Backend Testing

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.cameras

# Specific test class
python manage.py test apps.cameras.tests.CameraTestCase

# Specific test method
python manage.py test apps.cameras.tests.CameraTestCase.test_create_camera

# With coverage
coverage run --source='apps' manage.py test
coverage report
coverage html  # Generate HTML report

# With pytest (more detailed)
pytest apps/cameras/tests.py -v
pytest apps/cameras/tests.py::test_camera_creation -v
```

### Docker-based Testing

```bash
# Run tests in Docker
docker compose exec backend python manage.py test

# With coverage in Docker
docker compose exec backend coverage run --source='apps' manage.py test
docker compose exec backend coverage report
```

## Backend Test Structure

### Test File Organization

```
backend/apps/
├── cameras/
│   └── tests.py
│       • test_models.py
│       • test_serializers.py
│       • test_views.py
│       • test_permissions.py
│       • test_tasks.py
```

### Writing Tests

#### Model Tests

```python
# apps/cameras/tests/test_models.py
from django.test import TestCase
from apps.cameras.models import Camera
from apps.organizations.models import Organization
from apps.accounts.models import User

class CameraModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.org = Organization.objects.create(
            name='Test Org',
            created_by=self.user
        )
    
    def test_create_camera(self):
        """Test camera creation"""
        camera = Camera.objects.create(
            organization=self.org,
            name='Test Camera',
            connection_type='rtsp',
            host='192.168.1.100',
            port=554,
            stream_path='/stream1'
        )
        self.assertEqual(camera.name, 'Test Camera')
        self.assertEqual(camera.health_status, 'untested')
    
    def test_camera_default_values(self):
        """Test camera default field values"""
        camera = Camera.objects.create(
            organization=self.org,
            name='Default Test'
        )
        self.assertTrue(camera.is_enabled)
        self.assertFalse(camera.people_detection)
        self.assertEqual(camera.health_status, 'untested')
    
    def test_camera_url_generation(self):
        """Test RTSP URL generation"""
        camera = Camera.objects.create(
            organization=self.org,
            name='URL Test',
            connection_type='rtsp',
            host='192.168.1.100',
            port=554,
            username='admin',
            stream_path='/stream1'
        )
        expected_url = 'rtsp://admin:***@192.168.1.100:554/stream1'
        # Password encrypted, so check components
        self.assertIn('192.168.1.100', str(camera.get_stream_url()))
```

#### Serializer Tests

```python
# apps/cameras/tests/test_serializers.py
from rest_framework.test import APITestCase
from apps.cameras.serializers import CameraSerializer

class CameraSerializerTestCase(APITestCase):
    def setUp(self):
        # Setup test data
        pass
    
    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'name': 'Test Camera',
            'connection_type': 'rtsp',
            'host': '192.168.1.100',
            'port': 554
        }
        serializer = CameraSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_required_fields(self):
        """Test serializer with missing required fields"""
        data = {'name': 'Test Camera'}
        serializer = CameraSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('host', serializer.errors)
    
    def test_password_write_only(self):
        """Test that password is write-only"""
        data = {
            'name': 'Test',
            'password': 'secret123'
        }
        serializer = CameraSerializer(data=data)
        # Password should be accepted but not output
        self.assertNotIn('password', serializer.data)
```

#### API View Tests

```python
# apps/cameras/tests/test_views.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class CameraAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_cameras(self):
        """Test getting camera list"""
        response = self.client.get('/api/v1/cameras/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_create_camera(self):
        """Test creating a camera"""
        data = {
            'name': 'New Camera',
            'connection_type': 'rtsp',
            'host': '192.168.1.100',
            'port': 554
        }
        response = self.client.post('/api/v1/cameras/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Camera')
    
    def test_test_connection_endpoint(self):
        """Test camera connection testing"""
        data = {
            'connection_type': 'rtsp',
            'host': '192.168.1.100',
            'port': 554,
            'stream_path': '/stream1'
        }
        response = self.client.post('/api/v1/cameras/test_connection/', data)
        # May succeed or fail depending on actual camera
        self.assertIn(response.status_code, [200, 400])
        self.assertIn('success', response.data)
    
    def test_permission_required(self):
        """Test that authentication is required"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/cameras/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

#### Task Tests

```python
# apps/cameras/tests/test_tasks.py
from django.test import TestCase
from apps.cameras.tasks import check_camera_health
from apps.cameras.models import CameraHealthLog

class CameraTaskTestCase(TestCase):
    def setUp(self):
        # Create test camera
        pass
    
    def test_check_camera_health(self):
        """Test camera health check task"""
        result = check_camera_health()
        # Check that health logs were created
        logs = CameraHealthLog.objects.all()
        self.assertGreater(logs.count(), 0)
    
    @patch('apps.cameras.services.StreamConnectionTester.test_rtsp_stream')
    def test_health_check_updates_status(self, mock_test):
        """Test that health check updates camera status"""
        mock_test.return_value = {'success': True, 'error': None}
        check_camera_health()
        # Verify camera status was updated
```

## Frontend Testing

### Test Setup

```bash
# Create test file
# src/pages/__tests__/Dashboard.test.tsx

import { render, screen } from '@testing-library/react';
import { Dashboard } from '../Dashboard';

describe('Dashboard', () => {
  it('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });
});
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# With coverage
npm test -- --coverage

# Specific file
npm test Dashboard.test.tsx
```

## Integration Tests

### Full API Workflow Test

```python
# tests/integration/test_camera_workflow.py
from rest_framework.test import APITestCase
from rest_framework import status

class CameraWorkflowTestCase(APITestCase):
    """Test complete camera management workflow"""
    
    def test_camera_lifecycle(self):
        """Test: Create org → Add camera → Test connection → Get analytics"""
        
        # 1. Create user account
        user_data = {
            'email': 'workflow@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/register/', user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Login
        login_data = {
            'email': 'workflow@test.com',
            'password': 'testpass123'
        }
        response = self.client.post('/api/v1/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        
        # 3. Create organization
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        org_data = {
            'name': 'Integration Test Org',
            'privacy_confirmed': True
        }
        response = self.client.post('/api/v1/organizations/', org_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        org_id = response.data['id']
        
        # 4. Add camera
        camera_data = {
            'organization': org_id,
            'name': 'Integration Test Camera',
            'connection_type': 'rtsp',
            'host': '192.168.1.100',
            'port': 554,
            'username': 'admin',
            'password': 'password',
            'stream_path': '/stream1'
        }
        response = self.client.post('/api/v1/cameras/', camera_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        camera_id = response.data['id']
        
        # 5. Test connection
        test_data = {
            'connection_type': 'rtsp',
            'host': '192.168.1.100',
            'port': 554,
            'stream_path': '/stream1'
        }
        response = self.client.post('/api/v1/cameras/test_connection/', test_data)
        self.assertIn(response.status_code, [200, 400])
        
        # 6. Get camera details
        response = self.client.get(f'/api/v1/cameras/{camera_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Integration Test Camera')
```

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, constant

class APIUser(HttpUser):
    wait_time = constant(1)
    
    def on_start(self):
        # Login
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass'
        })
        self.token = response.json()['access']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    @task
    def list_cameras(self):
        self.client.get('/api/v1/cameras/', headers=self.headers)
    
    @task
    def list_events(self):
        self.client.get('/api/v1/events/', headers=self.headers)
    
    @task
    def list_analytics(self):
        self.client.get('/api/v1/analytics/summary/', headers=self.headers)
```

```bash
# Run load test
locust -f tests/performance/locustfile.py -u 100 -r 5 -t 1m
```

## Database Testing

### With Fixtures

```python
# tests/fixtures/test_data.json
[
  {
    "model": "accounts.user",
    "pk": 1,
    "fields": {
      "email": "test@example.com",
      "password": "hashed_password",
      "is_active": true
    }
  }
]

# Load in test
class MyTestCase(TestCase):
    fixtures = ['test_data.json']
```

### With Factory Boy

```python
# tests/factories.py
import factory
from apps.accounts.models import User
from apps.organizations.models import Organization

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization
    
    name = factory.Faker('company')
    created_by = factory.SubFactory(UserFactory)

# Use in tests
def test_something(self):
    user = UserFactory(email='custom@example.com')
    org = OrganizationFactory(created_by=user)
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: password
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python manage.py test

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: 18
      - run: cd frontend && npm ci
      - run: cd frontend && npm test
```

## Debugging Tests

### Using pytest with pdb

```bash
# Drop into debugger on failure
pytest -x -s --pdb

# Always drop into debugger
pytest --pdb
```

### Print Debugging in Tests

```python
def test_debug_example(self):
    response = self.client.get('/api/v1/cameras/')
    print("\n\nResponse data:")
    print(response.data)
    print("Response status:")
    print(response.status_code)
```

### Check Coverage Gaps

```bash
# Generate coverage report
coverage run --source='apps' manage.py test
coverage report --skip-covered

# HTML report
coverage html
# Open htmlcov/index.html in browser
```

## Test Checklist

**Backend Coverage:**
- [ ] Model creation and field validation
- [ ] Serializer validation
- [ ] API endpoint permissions
- [ ] API endpoint functionality
- [ ] Task execution
- [ ] Error handling
- [ ] Edge cases (empty results, invalid input)
- [ ] Database constraints

**Frontend Coverage:**
- [ ] Component rendering
- [ ] User interactions
- [ ] Form validation
- [ ] API integration
- [ ] Error states
- [ ] Loading states
- [ ] Navigation
- [ ] Responsive design

**Integration Coverage:**
- [ ] Complete workflows
- [ ] Multi-step processes
- [ ] Data consistency
- [ ] Permission boundaries

## Test Data Cleanup

Tests automatically clean up after themselves (Django TestCase rolls back transactions), but for performance:

```python
# Clear specific table
def setUp(self):
    Camera.objects.all().delete()

# Clear all test data
def tearDown(self):
    # Automatically handled by Django
    pass
```

## Performance Profiling

### Django Debug Toolbar

```python
# settings/local.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

Access at: http://localhost:8000/__debug__/

### Python Profiling

```python
import cProfile
import pstats

def profile_function():
    pr = cProfile.Profile()
    pr.enable()
    
    # Code to profile
    expensive_operation()
    
    pr.disable()
    ps = pstats.Stats(pr)
    ps.sort_stats('cumulative')
    ps.print_stats(20)
```

## Accessibility Testing

### Frontend Accessibility

```typescript
// Install testing-library accessibility testing
npm install --save-dev @testing-library/jest-dom

// Test accessibility
import { axe, toHaveNoViolations } from 'jest-axe';

test('page has no accessibility violations', async () => {
  const { container } = render(<Dashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Security Testing

### OWASP Testing

```python
# tests/security/test_authentication.py
class SecurityTestCase(APITestCase):
    def test_no_sql_injection(self):
        """Test SQL injection protection"""
        payload = "' OR '1'='1"
        response = self.client.get(f'/api/v1/events/?camera={payload}')
        # Should return 400 or empty, not SQL error
        self.assertNotIn('SQL', str(response.content))
    
    def test_csrf_protection(self):
        """Test CSRF token requirement"""
        self.client.logout()
        response = self.client.post('/api/v1/cameras/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_requirements(self):
        """Test password policy"""
        weak_passwords = ['123', 'abc', 'password']
        for pwd in weak_passwords:
            data = {
                'email': 'user@example.com',
                'password': pwd,
                'password_confirm': pwd
            }
            response = self.client.post('/api/v1/auth/register/', data)
            # Should reject weak passwords
            self.assertIn(response.status_code, [400])
```

## Conclusion

Maintain >80% code coverage and ensure all critical paths are tested. Run tests frequently during development and always before merging PRs.

For more information, see:
- Django Testing Documentation: https://docs.djangoproject.com/en/stable/topics/testing/
- pytest Documentation: https://docs.pytest.org/
- React Testing Library: https://testing-library.com/react
