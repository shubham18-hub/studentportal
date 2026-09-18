# CI/CD Setup & Automated Testing

## Overview

Automated testing is configured to run on every deployment. Tests validate:
- ✅ Backend API functionality
- ✅ Frontend build success
- ✅ Security (headers, rate limiting)
- ✅ Scalability (connection pooling)
- ✅ Integration (end-to-end flows)

---

## GitHub Actions Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Triggers**: Push to main/develop, PRs affecting `/backend`

**What it tests**:
- ✅ Python unit tests with pytest
- ✅ Code linting (flake8)
- ✅ Security scanning (bandit)
- ✅ Code coverage reporting
- ✅ MongoDB connectivity

**Runs**:
```
1. Starts MongoDB service (Docker)
2. Installs Python dependencies
3. Runs linting checks
4. Runs pytest test suite
5. Uploads coverage to Codecov
6. Security scans with bandit
```

### 2. Frontend Tests (`frontend-tests.yml`)

**Triggers**: Push to main/develop, PRs affecting `/frontend`

**What it tests**:
- ✅ Build success (npm run build)
- ✅ Output verification (dist folder)
- ✅ Dependencies audit (npm audit)
- ✅ Secret detection (trufflesecurity)
- ✅ Multiple Node versions (18.x, 20.x)

**Runs**:
```
1. Installs Node dependencies
2. Runs linting (if available)
3. Builds production bundle
4. Verifies dist directory created
5. Audits npm dependencies
6. Scans for exposed secrets
```

### 3. Integration Tests (`integration-tests.yml`)

**Triggers**: Push to main/develop, PRs to any branch

**What it tests**:
- ✅ Backend + Frontend together
- ✅ MongoDB integration
- ✅ Health checks
- ✅ API endpoints
- ✅ Full test suite

**Runs**:
```
1. Starts MongoDB
2. Installs backend and frontend
3. Configures environment
4. Starts backend service
5. Runs all pytest tests
6. Tests API endpoints directly
7. Collects logs on failure
```

### 4. Deploy to Render (`deploy-render.yml`)

**Triggers**: Push to main branch, manual workflow dispatch

**What it does**:
- ✅ Runs all tests (same as integration)
- ✅ Validates production configuration
- ✅ Uses production environment variables
- ✅ Triggers Render webhook on success

**Runs**:
```
1. Runs backend tests
2. Runs frontend build
3. Verifies all tests pass
4. Deploys to Render.com (via webhook)
```

---

## Setup Instructions

### Step 1: Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/studentportal.git
git branch -M main
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

```
GOOGLE_CLIENT_ID          = your-google-client-id
GOOGLE_CLIENT_SECRET      = your-google-client-secret
ADMIN_EMAIL               = admin@ecell.com
ADMIN_PASSWORD_HASH       = $2b$12$bcrypt_hash_here
FRONTEND_URL              = https://yourdomain.com
RENDER_DEPLOY_WEBHOOK     = https://api.render.com/deploy/...
```

**How to generate ADMIN_PASSWORD_HASH**:
```bash
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('YourPassword123!'))"
```

### Step 3: Configure Render Webhook

1. Go to Render Dashboard
2. Select your service
3. **Settings** → **Deploy Hook**
4. Copy the webhook URL
5. Add to GitHub Secrets as `RENDER_DEPLOY_WEBHOOK`

### Step 4: Verify Workflows

Go to **Actions** tab in GitHub:
- [ ] See `backend-tests.yml` listed
- [ ] See `frontend-tests.yml` listed
- [ ] See `integration-tests.yml` listed
- [ ] See `deploy-render.yml` listed

---

## Test Execution Flow

### On Every Push to main/develop

```
Push → GitHub Actions
       ├─ Backend Tests (5 min)
       │  ├─ Linting
       │  ├─ Unit tests
       │  ├─ Coverage
       │  └─ Security scan
       │
       ├─ Frontend Tests (3 min)
       │  ├─ Build
       │  ├─ Audit
       │  └─ Secret scan
       │
       └─ Integration Tests (7 min)
          ├─ Start services
          ├─ Run all tests
          ├─ Test endpoints
          └─ Collect artifacts
```

**Total Time**: ~15 minutes

### On Push to main (After All Tests Pass)

```
All Tests Pass
       ↓
Deploy Workflow
       ├─ Run all tests again
       └─ Trigger Render Deploy
              ↓
         Render Deployment
              ├─ Build backend
              ├─ Build frontend
              └─ Deploy services
              
Deployment Complete (5-10 min)
```

---

## What Gets Tested

### Backend Tests

```python
✅ Authentication
   - Admin login (valid/invalid)
   - Google OAuth flow
   - Token verification
   - Logout

✅ Security
   - Security headers present
   - Rate limiting works
   - CORS configured
   - Input validation

✅ Scalability
   - Connection pool size
   - Database indexes
   - Concurrent connections

✅ API Endpoints
   - Task CRUD operations
   - Submission workflow
   - Grading system
   - Analytics
```

### Frontend Tests

```
✅ Build
   - No build errors
   - dist/ created
   - All assets bundled

✅ Dependencies
   - npm audit passes
   - No vulnerable deps

✅ Security
   - No exposed secrets
   - No API keys hardcoded
```

### Integration Tests

```
✅ End-to-End
   - Backend starts
   - Frontend builds
   - Health check passes
   - API responds
   - MongoDB connected
```

---

## Viewing Test Results

### GitHub Actions Dashboard

1. Go to **Actions** tab
2. Click on the workflow run
3. See detailed logs for each step
4. Download artifacts (logs, reports)

### Test Reports

Each workflow generates:
- **Coverage Report**: Code coverage percentage
- **Security Report**: Bandit findings
- **Build Artifacts**: dist/ folder
- **Logs**: Test output

### On Failure

If tests fail:
1. Click on the failed job
2. Scroll to failed step
3. Read error message
4. Fix code locally
5. Push changes (runs tests again)

---

## Local Testing (Before Push)

### Run Backend Tests Locally

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up test environment
export MONGODB_URI=mongodb://localhost:27017/ecell_test
export ENVIRONMENT=testing

# Run tests
pytest tests/ -v

# Generate coverage report
pytest tests/ --cov=app --cov-report=html
# Open: htmlcov/index.html
```

### Run Frontend Tests Locally

```bash
cd frontend

# Install dependencies
npm ci

# Build
npm run build

# Audit dependencies
npm audit
```

### Run Integration Tests Locally

```bash
# Terminal 1: Start MongoDB
mongod

# Terminal 2: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 3: Run tests
cd backend
pytest tests/ -v
```

---

## Deployment Flow

### Automated Deployment (After Push to main)

```
1. Push to main
2. All tests run (15 min)
3. If tests pass:
   - Render webhook triggered
   - Backend builds (5 min)
   - Frontend builds (5 min)
   - Services deploy (2 min)
   - Health check passes
   - ✅ Live on render.com

4. If tests fail:
   - Deployment blocked
   - Developer notified
   - Fix required before retry
```

### Manual Deployment

```bash
# If you need to deploy without changes:
1. Go to Actions → deploy-render.yml
2. Click "Run workflow"
3. Select branch (main)
4. Click "Run workflow"
5. Wait for completion
```

---

## Monitoring Deployments

### Health Checks

After deployment, verify:

```bash
# Health check
curl https://yourdomain-backend.onrender.com/health

# API docs
https://yourdomain-backend.onrender.com/docs

# Frontend
https://yourdomain.onrender.com
```

### Logs

View logs in:
1. **Render Dashboard** → Service → Logs tab
2. **GitHub Actions** → Workflow run → Logs

### Rollback on Failure

If deployment fails:
1. Render automatically keeps previous version
2. Check logs for error
3. Fix code locally
4. Push again (triggers tests + redeploy)

---

## Troubleshooting CI/CD

### Issue: Tests Fail Locally But Pass in CI

**Solution**:
- Use same Python/Node versions as CI
- Match environment variables
- Check for timezone issues
- Use UTC in tests

### Issue: MongoDB Tests Timeout

**Solution**:
- Increase timeout in workflow
- Check MongoDB health check
- Verify Docker is running

### Issue: Secrets Not Recognized

**Solution**:
- Check secret names match exactly
- Verify in **Settings** → **Secrets**
- Redeploy after adding secret

### Issue: Render Webhook Not Triggering

**Solution**:
- Verify webhook URL in secrets
- Check Render dashboard for webhook logs
- Re-generate webhook if needed
- Test manually via Actions tab

---

## Performance Notes

### Test Timing

- Backend tests: 5 minutes
- Frontend tests: 3 minutes
- Integration tests: 7 minutes
- Build/Deploy: 10-15 minutes
- **Total**: 25-30 minutes from push to live

### Optimization Tips

1. **Parallelize**: Tests run in parallel where possible
2. **Cache**: npm and pip caching reduces install time
3. **Shallow Clone**: GitHub provides shallow repos
4. **Matrix Strategy**: Test multiple Node versions simultaneously

---

## Success Criteria

✅ **All workflows visible** in Actions tab
✅ **Tests pass** on push to main
✅ **Deployment triggered** after tests pass
✅ **Services live** on Render.com
✅ **Health checks** responding
✅ **No manual deployment** needed

---

## Example Workflow Status

```
✅ backend-tests.yml     PASSED
✅ frontend-tests.yml    PASSED
✅ integration-tests.yml PASSED
✅ deploy-render.yml     PASSED (Deployment triggered)

🎉 System live at https://yourdomain.onrender.com
```

---

## Next Steps

1. Push code to GitHub
2. Watch Actions tab for test runs
3. Verify all workflows pass
4. Confirm deployment to Render
5. Test production URL

---

**Automated Testing Status**: ✅ **CONFIGURED & READY**

Every deployment is automatically tested before going live!
