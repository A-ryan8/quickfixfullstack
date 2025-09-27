# Test Pipeline Documentation

## Overview
This document describes the testing pipeline for the Civic Complaint Management API.

## Test Categories

### 1. Unit Tests
- **Purpose**: Test individual functions and methods
- **Coverage**: Database operations, API endpoints, business logic
- **Tools**: pytest, unittest

### 2. Integration Tests
- **Purpose**: Test interaction between components
- **Coverage**: Database connections, API endpoints, external services
- **Tools**: pytest, requests

### 3. End-to-End Tests
- **Purpose**: Test complete user workflows
- **Coverage**: Full application flow from frontend to backend
- **Tools**: Selenium, Playwright

## Test Structure

```
tests/
├── unit/
│   ├── test_database.py
│   ├── test_models.py
│   ├── test_prioritization.py
│   └── test_security.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_database_integration.py
│   └── test_firebase_integration.py
├── e2e/
│   ├── test_complaint_workflow.py
│   ├── test_admin_workflow.py
│   └── test_user_workflow.py
└── fixtures/
    ├── sample_complaints.json
    ├── test_users.json
    └── mock_responses.json
```

## Test Data

### Sample Complaints
```json
{
  "complaints": [
    {
      "id": 1,
      "title": "Pothole on Main Street",
      "description": "Large pothole causing traffic issues",
      "location": "Main Street, Downtown",
      "status": "pending",
      "upvote_count": 15,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Test Users
```json
{
  "users": [
    {
      "email": "admin@test.com",
      "role": "admin",
      "uid": "admin_uid_123"
    },
    {
      "email": "user@test.com",
      "role": "user",
      "uid": "user_uid_456"
    }
  ]
}
```

## Test Execution

### Local Testing
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=backend --cov-report=html
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Test Scenarios

### 1. Complaint Management
- Create complaint
- Update complaint status
- Delete complaint
- Get complaint details
- List complaints with pagination

### 2. User Authentication
- Login with valid credentials
- Login with invalid credentials
- Token validation
- Role-based access control

### 3. Prioritization Algorithm
- Calculate priority scores
- Sort complaints by priority
- Handle edge cases (no upvotes, old complaints)

### 4. File Upload
- Upload image files
- Upload PDF files
- Handle invalid file types
- Handle large files

## Performance Tests

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/complaints/public

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/complaints/public
```

### Stress Testing
- High concurrent requests
- Large file uploads
- Database connection limits
- Memory usage monitoring

## Test Reports

### Coverage Report
- HTML coverage report generated in `htmlcov/`
- Minimum coverage threshold: 80%
- Exclude test files and configuration files

### Performance Report
- Response time metrics
- Throughput measurements
- Resource usage statistics
- Error rate analysis

## Continuous Integration

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks
pre-commit run --all-files
```

### Automated Testing
- Run tests on every commit
- Run tests on pull requests
- Deploy to staging on successful tests
- Deploy to production on main branch

## Test Environment

### Database
- Use test database for integration tests
- Reset database state between tests
- Use transactions for test isolation

### External Services
- Mock Firebase authentication
- Mock Gemini AI API
- Use test API keys

### Configuration
```env
# Test environment variables
TEST_DB_HOST=localhost
TEST_DB_NAME=civic_complaints_test
TEST_FIREBASE_PROJECT_ID=test-project
TEST_GEMINI_API_KEY=test-key
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure test database is running
2. **Firebase Auth**: Check test project configuration
3. **File Permissions**: Ensure test files are writable
4. **Port Conflicts**: Use different ports for test server

### Debug Mode
```bash
# Run tests with verbose output
pytest -v -s

# Run specific test with debug
pytest tests/unit/test_database.py::test_create_complaint -v -s
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Cleanup**: Clean up test data after each test
3. **Mocking**: Mock external dependencies
4. **Assertions**: Use specific assertions
5. **Documentation**: Document test scenarios
6. **Maintenance**: Keep tests up to date with code changes
