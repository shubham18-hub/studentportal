# Testing Guide

This guide covers testing the E-Cell Task Portal backend and frontend.

## Backend Testing

### 1. Setup Backend Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure .env

Edit `backend/.env`:
```env
MONGODB_URI=mongodb://localhost:27017/ecell  # Local MongoDB
SECRET_KEY=test-secret-key-min-32-characters-long
GOOGLE_CLIENT_ID=test-client-id
GOOGLE_CLIENT_SECRET=test-client-secret
ADMIN_EMAIL=admin@test.com
ADMIN_PASSWORD_HASH=$2b$12$YOUR_BCRYPT_HASH_HERE
ALLOWED_DOMAINS=test.com,example.com
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

**Generate admin password hash**:
```bash
python3 -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['bcrypt']); print(pwd.hash('testpassword'))"
```

### 3. Start MongoDB

**Using Docker**:
```bash
docker run -d -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=password mongo:7.0
```

**Or install locally** and start MongoDB service.

### 4. Run Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### 5. Test API Endpoints

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

**Key endpoints to test**:

#### Authentication
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/google` - Google OAuth login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

#### Tasks (Admin)
- `POST /api/tasks/` - Create task
- `GET /api/tasks/admin/all` - Get all tasks
- `GET /api/tasks/{task_id}` - Get task details
- `PUT /api/tasks/{task_id}` - Update task
- `DELETE /api/tasks/{task_id}` - Delete task

#### Tasks (Participant)
- `GET /api/tasks/participant/by-stage/{stage}` - Get tasks by stage
- `GET /api/tasks/participant/all` - Get all tasks with submission status

#### Submissions
- `POST /api/tasks/submissions/{task_id}` - Create/update submission
- `GET /api/tasks/submissions/{task_id}` - Get user's submission
- `GET /api/tasks/admin/submissions/{task_id}` - Get all submissions for task
- `POST /api/tasks/submissions/{submission_id}/grade` - Grade submission

#### Analytics
- `GET /api/tasks/admin/analytics` - Get dashboard analytics

### 6. Manual Test Scenarios

#### Scenario 1: Admin Login
1. POST to `/api/auth/admin/login` with:
   ```json
   {
     "email": "admin@test.com",
     "password": "testpassword"
   }
   ```
2. Receive token and user info
3. Use token for admin endpoints

#### Scenario 2: Create and View Task
1. Admin creates task via POST `/api/tasks/`
2. Participant fetches task via GET `/api/tasks/participant/all`
3. Verify task appears in correct workflow stage

#### Scenario 3: Submit and Grade
1. Participant submits file via POST `/api/tasks/submissions/{task_id}`
2. Admin retrieves submissions via GET `/api/tasks/admin/submissions/{task_id}`
3. Admin grades via POST `/api/tasks/submissions/{submission_id}/grade`
4. Participant fetches their submission and sees grade

---

## Frontend Testing

### 1. Setup Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
```

### 2. Configure .env.local

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-test-client-id.apps.googleusercontent.com
```

### 3. Run Frontend Development Server

```bash
npm run dev
```

Frontend runs at `http://localhost:5173` (or `http://localhost:3000` with Vite config)

### 4. Test Features

#### Login Page
- [ ] Google OAuth button displays
- [ ] Admin login tab switches
- [ ] Email/password form validates
- [ ] Error messages display on failure
- [ ] Theme toggle works

#### Dashboard (Participant)
- [ ] All workflow stages visible
- [ ] Stage selector filters tasks correctly
- [ ] Task cards show title, deadline, points
- [ ] Task cards show submission status
- [ ] Can click to view task details

#### Task Detail
- [ ] Task info displays (title, description, guidelines)
- [ ] Deadline and points shown
- [ ] Current submission visible if submitted
- [ ] File upload drag-and-drop works
- [ ] File validation (PDF only, max 10MB)
- [ ] Submit button disabled without file
- [ ] Success message on submission

#### Admin Dashboard
- [ ] Analytics cards display correct numbers
- [ ] Stage selector filters tasks
- [ ] Create Task button navigates to form
- [ ] Click task navigates to submissions page

#### Create Task
- [ ] Form fields validate
- [ ] Stage selector shows all three stages
- [ ] Deadline picker works
- [ ] Submit creates task and redirects
- [ ] Cancel button works

#### Grade Submissions
- [ ] All submissions listed
- [ ] Click "Grade" shows form
- [ ] Points input validates
- [ ] Feedback textarea works
- [ ] Submit grades updates status
- [ ] Graded submissions show points

#### Theme
- [ ] Toggle between light/dark modes
- [ ] Dark mode applies dark backgrounds
- [ ] Blue accents visible in both themes
- [ ] Preference persists on refresh

#### Responsive
- [ ] Mobile: All content visible at 375px
- [ ] Tablet: Sidebar/drawer visible
- [ ] Desktop: Multi-column layout works
- [ ] Touch targets large enough (44px+)

---

## Integration Testing

### 1. Full User Journey - Admin

1. Admin logs in
2. Creates a task in "Preliminary" stage
3. Verifies task appears in dashboard
4. Logs out
5. Logs back in as admin
6. Navigates to submissions page
7. Views submissions (empty initially)

### 2. Full User Journey - Participant

1. Participant logs in with Google OAuth
2. Sees dashboard with available tasks
3. Filters tasks by stage
4. Clicks a task to view details
5. Reads guidelines
6. Uploads a PDF file
7. Submits task
8. Sees submission status change
9. Logs out and logs back in
10. Verifies submission persists
11. Sees graded feedback if available

### 3. Grading Workflow

1. Admin creates task
2. Participant submits file
3. Admin navigates to submissions
4. Grades submission with points and feedback
5. Participant views grade and feedback
6. Analytics dashboard updates

---

## Performance Testing

### Load Testing
```bash
# Install Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Test API endpoint
ab -n 1000 -c 10 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/tasks/admin/all
```

### Frontend Build
```bash
cd frontend
npm run build
```

Check:
- Build completes without errors
- dist/ folder created
- No console warnings

---

## Debugging

### Backend Logs
```bash
# See detailed logs
uvicorn app.main:app --reload --log-level debug
```

### Frontend Console
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls
- Check Application tab for stored tokens

### MongoDB Connection
```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017" -u admin -p password
db.admin.command('ping')
```

---

## Docker Testing

### Test with Docker Compose
```bash
docker-compose up
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- MongoDB: localhost:27017

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Stop Services
```bash
docker-compose down
```

---

## Checklist Before Production

- [ ] All API endpoints working
- [ ] Authentication (Google OAuth + admin) working
- [ ] Tasks CRUD operations working
- [ ] Submissions working
- [ ] Grading workflow complete
- [ ] Frontend builds without errors
- [ ] Responsive design works on mobile
- [ ] Dark/light theme toggle works
- [ ] Environment variables properly set
- [ ] MongoDB connection secure
- [ ] CORS configured correctly
- [ ] Error handling works
- [ ] No sensitive data in logs
- [ ] API rate limiting configured
- [ ] Admin password properly hashed
- [ ] Google OAuth credentials valid
