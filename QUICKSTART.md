# Quick Start Guide

Get the E-Cell Task Portal running in 5 minutes.

## Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)
- Git

## Option 1: Docker Compose (Recommended)

Fastest way to get everything running:

```bash
# Clone repository
git clone <repo-url>
cd studentportal

# Copy environment file
cp .env.example .env

# Edit .env with your credentials
# - GOOGLE_CLIENT_ID
# - GOOGLE_CLIENT_SECRET
# - ADMIN_PASSWORD_HASH (generate with: python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('yourpassword'))")
# - MONGODB_URI (or use local MongoDB on port 27017)

# Start everything
docker-compose up

# Wait 30 seconds for services to start
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Option 2: Local Development

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your settings
# Make sure MongoDB is running:
# - Local: mongod (starts on localhost:27017)
# - Or Atlas: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ecell

# Start backend
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### 2. Frontend Setup (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Edit .env.local
# VITE_API_URL=http://localhost:8000
# VITE_GOOGLE_CLIENT_ID=your-client-id

# Start frontend
npm run dev
```

Frontend runs at http://localhost:5173 or http://localhost:3000

## First Time Setup

### Create Admin Account

1. Generate password hash:
```bash
python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('YourAdminPassword123!'))"
```

2. Add to `.env`:
```
ADMIN_EMAIL=admin@ecell.com
ADMIN_PASSWORD_HASH=<paste-hash-from-above>
```

### Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:3000`
   - `http://localhost:5173`
   - `https://yourdomain.com` (production)
6. Copy Client ID and Client Secret to `.env`

## Test Users

### Admin Login
- Email: `admin@ecell.com`
- Password: Whatever you set above

### Student Login
- Use Google OAuth with any email from:
  - `@klecba.edu.in`
  - `@kle.ac.in`
  - `@klecba.edu`

## Verify Everything Works

### Backend
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

### Frontend
- Visit http://localhost:3000 (or 5173)
- Should see login page
- Try logging in

### API Documentation
- Visit http://localhost:8000/docs
- Try endpoints with "Try it out" button

## Common Issues

### "Cannot connect to MongoDB"
- Ensure MongoDB is running: `mongod`
- Or update MONGODB_URI in .env

### "Google login not working"
- Check GOOGLE_CLIENT_ID is correct
- Verify localhost:3000 (or 5173) is in OAuth redirect URIs
- Check browser console for errors

### "Admin login not working"
- Ensure ADMIN_PASSWORD_HASH is set in .env
- Password must match the hash
- Restart backend after changing .env

### "Port already in use"
- Backend: Change port in backend/app/main.py (default 8000)
- Frontend: Change port in frontend/vite.config.ts (default 3000/5173)

## Next Steps

- **Testing**: See TESTING.md for detailed test scenarios
- **Deployment**: See DEPLOYMENT.md for Render setup
- **Privacy**: See PRIVACY.md for data handling policies
- **Verification**: See VERIFICATION.md for pre-production checklist

## Useful Commands

```bash
# Backend tests
cd backend
pytest tests/

# Frontend build
cd frontend
npm run build

# Load testing
python3 scripts/load-test.py

# Docker cleanup
docker-compose down -v  # Removes volumes too

# Restart services
docker-compose restart

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Architecture

```
Frontend (React)
    ↓ HTTP/HTTPS
Backend (FastAPI)
    ↓
MongoDB (Database)
```

## Features

✓ Google OAuth + Admin login
✓ Role-based access (Admin, Student, Faculty)
✓ Task management (CRUD)
✓ Workflow stages (Preliminary, Ignite Propel, Comprehensive)
✓ PDF submissions
✓ Grading system
✓ Analytics dashboard
✓ Dark/light theme
✓ Responsive design
✓ 1000+ student capacity
✓ Privacy-first architecture

## Support

- API Issues: Check http://localhost:8000/docs
- Frontend Issues: Check browser console (F12)
- Database Issues: Check MongoDB logs
- Detailed Testing: See TESTING.md
- Deployment Help: See DEPLOYMENT.md

## Documentation

- **README.md** - Project overview
- **QUICKSTART.md** - This file
- **TESTING.md** - Test procedures
- **DEPLOYMENT.md** - Production deployment
- **PRIVACY.md** - Privacy & security policies
- **VERIFICATION.md** - Pre-production checklist

---

**Ready to go!** 🚀

Questions? Check the relevant documentation file above.
