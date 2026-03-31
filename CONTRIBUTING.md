# Contributing to CCTV Analytics SaaS

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on code quality and user experience
- No harassment or discriminatory language

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL (for local development)
- Redis (for local cache/queue testing)

### Development Setup

1. **Clone and setup**
```bash
git clone https://github.com/yourusername/cctv-analytics.git
cd cctv-analytics
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

2. **Configure environment**
```bash
cp .env.example .env
# Update .env with local values
```

3. **Run migrations**
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

4. **Start servers** (in separate terminals)
```bash
# Backend
cd backend && python manage.py runserver

# Frontend
cd frontend && npm run dev

# Celery worker
cd backend && celery -A config worker -l info

# Celery beat
cd backend && celery -A config beat -l info
```

## Development Workflow

### Branching Strategy
```
main (stable, production-ready)
├── develop (integration branch)
│   ├── feature/camera-discovery
│   ├── feature/stripe-integration
│   ├── bugfix/health-check-timeout
│   └── docs/api-documentation
```

**Branch Naming:**
- Feature: `feature/short-description`
- Bug: `bugfix/short-description`
- Docs: `docs/short-description`
- Testing: `test/short-description`

### Commit Message Format
```
type(scope): brief description

Detailed explanation of what changed and why.
Mention any related issues: Closes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Build tools, dependencies

**Example:**
```
feat(cameras): add ONVIF camera discovery

- Implement ONVIFCamera class with device scanning
- Add discovery endpoint /api/v1/cameras/discover/
- Support for credential-based stream URI extraction

Closes #456
```

## Making Changes

### Backend Changes (Django)

**Adding a new feature:**

1. **Create serializers** (`backend/apps/xxx/serializers.py`)
```python
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'created_at']
```

2. **Create viewsets** (`backend/apps/xxx/views.py`)
```python
from rest_framework.viewsets import ModelViewSet
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
```

3. **Add URL routing** (`backend/apps/xxx/urls.py`)
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyModelViewSet

router = DefaultRouter()
router.register('mymodels', MyModelViewSet)

urlpatterns = [path('', include(router.urls))]
```

4. **Write tests** (`backend/apps/xxx/tests.py`)
```python
from django.test import TestCase
from rest_framework.test import APIClient

class MyModelTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_create_model(self):
        response = self.client.post('/api/v1/mymodels/', {
            'name': 'Test'
        })
        self.assertEqual(response.status_code, 201)
```

**Code Standards:**
- Follow PEP 8 (use `black` for formatting)
- Add docstrings to functions and classes
- Use type hints for function arguments
- Keep functions focused and under 50 lines
- Use Django ORM properly (avoid N+1 queries)

### Frontend Changes (React/TypeScript)

**Adding a new page:**

1. **Create component** (`frontend/src/pages/NewPage.tsx`)
```typescript
import React from 'react';
import { useNavigate } from 'react-router-dom';

export const NewPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold">New Page</h1>
    </div>
  );
};
```

2. **Add route** (`frontend/src/App.tsx`)
```typescript
import { NewPage } from './pages/NewPage';

export const App = () => (
  <Routes>
    <Route path="/new-page" element={<NewPage />} />
  </Routes>
);
```

3. **Update navigation** (`frontend/src/components/Navbar.tsx`)

**Code Standards:**
- Use TypeScript strictly (no `any` types)
- Functional components with hooks
- Preferentially use existing components
- Props should be typed interfaces
- Keep components under 200 lines
- Use Tailwind classes for styling
- Follow React best practices (memoization, keys, etc.)

## Testing

### Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test apps.cameras

# With coverage
coverage run --source='apps' manage.py test
coverage report
```

**Test structure:**
```python
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from .models import MyModel

class MyModelAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('test@example.com', 'pass')
        self.client.force_authenticate(user=self.user)
    
    def test_list_models(self):
        MyModel.objects.create(name='Test')
        response = self.client.get('/api/v1/mymodels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
```

### Frontend Tests

```bash
# Run tests
npm test

# Watch mode
npm test -- --watch
```

**Using Vitest + React Testing Library:**
```typescript
import { render, screen } from '@testing-library/react';
import { NewPage } from './NewPage';

describe('NewPage', () => {
  it('renders heading', () => {
    render(<NewPage />);
    expect(screen.getByText('New Page')).toBeInTheDocument();
  });
});
```

## Documentation

### Adding Documentation

1. **Code comments:**
   - Use docstrings for all public functions
   - Explain "why", not "what"
   
   ```python
   def calculate_occupancy(people_count: int, room_capacity: int) -> float:
       """
       Calculate room occupancy percentage.
       
       Args:
           people_count: Number of people currently in room
           room_capacity: Maximum capacity of room
       
       Returns:
           Occupancy as percentage (0-100)
       
       Raises:
           ValueError: If capacity is 0
       """
       if room_capacity == 0:
           raise ValueError("Capacity must be > 0")
       return (people_count / room_capacity) * 100
   ```

2. **API Documentation:**
   - Update docstrings in viewsets
   - Swagger/OpenAPI auto-generates from these

   ```python
   class MyModelViewSet(ModelViewSet):
       """
       MyModel API endpoint.
       
       list: Get all models
       create: Create new model
       retrieve: Get specific model
       """
   ```

3. **User Guides:**
   - Add to `docs/` folder with clear steps
   - Include screenshots where helpful
   - Provide examples

## Submitting Changes

### Pull Request Process

1. **Before submitting:**
   ```bash
   # Update your branch
   git fetch origin
   git rebase origin/main
   
   # Ensure tests pass
   python manage.py test
   npm test
   
   # Format code
   black backend/
   npx prettier --write frontend/
   ```

2. **Create PR:**
   - Push your feature branch
   - Open PR with descriptive title
   - Reference related issues
   - Add description of changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Related Issue
   Closes #123
   
   ## Changes Made
   - Item 1
   - Item 2
   
   ## Testing
   How did you test these changes?
   
   ## Checklist
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] No breaking changes
   - [ ] Backwards compatible
   ```

4. **Review process:**
   - At least 1 maintainer approval
   - All CI checks must pass
   - Coverage should not decrease
   - Resolve conflicts/comments

### CI/CD Checks

All PRs must pass:
- Python linting (flake8, black)
- TypeScript checking (eslint, tsc)
- All tests passing
- No type errors
- Code coverage maintained

## Performance Guidelines

### Backend
- Avoid N+1 queries: use `select_related()`, `prefetch_related()`
- Cache frequently accessed data
- Index database fields used in filters
- Limit queryset results with pagination
- Use database transactions for consistency

### Frontend
- Code split large bundles
- Lazy load routes
- Memoize expensive components
- Optimize re-renders
- Use virtual lists for large datasets

### AI/Vision
- Process every Nth frame (configurable)
- Use model quantization for speed
- Batch process frames where possible
- Profile with `cProfile` before optimizing

## Security Considerations

When making changes, ensure:
- ✅ No credentials in code/config
- ✅ All user inputs validated and sanitized
- ✅ Authentication required for sensitive endpoints
- ✅ Authorization checks in place
- ✅ SQL injection prevention (use ORM)
- ✅ CSRF protection on state-changing operations
- ✅ Rate limiting on public endpoints
- ✅ No sensitive data in logs

## Reporting Issues

**Bug Report Template:**
```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows/Linux/macOS
- Python: 3.11+
- Docker: Yes/No
- Logs: [attached]
```

## Feature Request Template

```markdown
## Description
What feature would you like?

## Use Case
Why is this needed?

## Proposed Solution
How should it work?

## Alternative Solutions
Other approaches considered

## Additional Context
Screenshots, examples, etc.
```

## Development Tips

### Useful Commands

```bash
# Backend
python manage.py shell           # Django shell for testing
python manage.py graph_models    # Visualize models
python manage.py showmigrations  # View migration status

# Frontend
npm run type-check  # Full TypeScript check
npm run build      # Production build
npm run preview    # Preview prod build

# Docker
docker compose logs -f backend
docker compose exec backend bash
docker compose up --build
```

### Debugging

**Backend:**
```python
import pdb
pdb.set_trace()  # Breakpoint

# Or use debugger=True in settings for detailed errors
```

**Frontend:**
```typescript
debugger;  // Breakpoint in browser console

// Or use VS Code debugger
```

### Profiling

**Backend Performance:**
```bash
pip install django-debug-toolbar
# Add to INSTALLED_APPS, run with DEBUG=True
```

**Frontend Performance:**
```bash
npm run build -- --analyze
```

## Architecture Decisions

Before making architectural changes, consider:
- Impact on existing code and features
- Backwards compatibility
- Performance implications
- Security considerations
- Test coverage changes
- Documentation updates needed

Create an ADR (Architecture Decision Record) in `docs/adr/` for significant changes.

## Release Process

Contributors don't need to worry about releases, but for maintainers:

```bash
# Bump version in package.json and setup.py
# Update CHANGELOG.md
git tag v1.2.3
git push origin v1.2.3
# CI/CD builds and releases to PyPI, NPM, Docker Hub
```

## Resources

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **React Docs**: https://react.dev/
- **TypeScript Docs**: https://www.typescriptlang.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **YOLOv8**: https://docs.ultralytics.com/

## Getting Help

- Check existing issues and documentation
- Ask in GitHub Discussions
- Email maintainers at dev@example.com
- Join our Slack community

## Thank You!

Every contribution, no matter how small, helps improve the project. Your efforts are greatly appreciated! 🎉
