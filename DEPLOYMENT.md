# Deployment Guide

This document covers deploying the E-Cell Task Portal to production using Render.com and MongoDB Atlas.

## Prerequisites

- Render.com account
- MongoDB Atlas account (free tier available)
- Google OAuth 2.0 credentials
- GitHub repository with the code

## MongoDB Atlas Setup

1. **Create a Cluster**:
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free tier cluster
   - Choose a region close to your users
   - Wait for cluster to be ready

2. **Create Database User**:
   - Go to Database Access
   - Click "Add New Database User"
   - Create a username and password
   - Select "Autogenerate Secure Password"
   - Add user

3. **Get Connection String**:
   - Go to Clusters > Connect
   - Choose "Drivers"
   - Select "Node.js" driver and latest version
   - Copy the connection string
   - Replace `<password>` with your database password
   - Replace `<dbname>` with `ecell`

4. **Whitelist IP**:
   - Go to Network Access
   - Click "Add IP Address"
   - Select "Allow access from anywhere" (0.0.0.0/0)
   - Confirm

## Render.com Setup

### Option 1: Using render.yaml (Recommended)

1. **Connect GitHub**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +"
   - Select "Blueprint"
   - Connect your GitHub account
   - Select your repository

2. **Configure Environment Variables**:
   - Before deploying, set all required environment variables in Render settings:
   - `MONGODB_URI`: Connection string from MongoDB Atlas
   - `SECRET_KEY`: Generate a random 32+ character string
   - `GOOGLE_CLIENT_ID`: From Google Cloud Console
   - `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
   - `ADMIN_EMAIL`: Admin login email
   - `ADMIN_PASSWORD_HASH`: Hashed admin password (see below)
   - `FRONTEND_URL`: Your frontend Render URL

3. **Generate Admin Password Hash**:
   ```bash
   python3 -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['bcrypt']); print(pwd.hash('your_password'))"
   ```

4. **Deploy**:
   - Click "Deploy Blueprint"
   - Services will be created automatically
   - Monitor build logs

### Option 2: Manual Setup

1. **Backend Service**:
   - Click "New +" > "Web Service"
   - Connect GitHub repository
   - Set build command: `cd backend && pip install -r requirements.txt`
   - Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Set health check path: `/health`
   - Add environment variables (see above)
   - Deploy

2. **Frontend Service**:
   - Click "New +" > "Web Service"
   - Connect GitHub repository
   - Set build command: `cd frontend && npm install && npm run build`
   - Set start command: `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     - `VITE_API_URL`: Backend service URL (e.g., https://ecell-backend.onrender.com)
     - `VITE_GOOGLE_CLIENT_ID`: Same as backend
   - Deploy

3. **Connect Services**:
   - Update frontend's `VITE_API_URL` to point to backend service URL
   - Redeploy frontend

## Environment Variables Summary

### Backend (.env)
```
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/ecell
SECRET_KEY=your-very-secret-key-32-chars-minimum
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
ADMIN_EMAIL=admin@ecell.com
ADMIN_PASSWORD_HASH=$2b$12$bcrypt_hash_here
ALLOWED_DOMAINS=klecba.edu.in,kle.ac.in,klecba.edu
FRONTEND_URL=https://ecell-frontend.onrender.com
ENVIRONMENT=production
```

### Frontend (.env.local)
```
VITE_API_URL=https://ecell-backend.onrender.com
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

## Monitoring and Maintenance

1. **View Logs**:
   - Go to service > Logs tab
   - Monitor for errors

2. **Health Checks**:
   - Backend health: `https://ecell-backend.onrender.com/health`
   - API docs: `https://ecell-backend.onrender.com/docs`

3. **Database Backups**:
   - MongoDB Atlas provides automatic backups
   - Configure backup frequency in Atlas dashboard

4. **Scaling**:
   - Upgrade Render plan for better performance
   - Configure auto-scaling if needed

## Troubleshooting

### Build Fails
- Check build logs for errors
- Verify all dependencies in requirements.txt
- Ensure GitHub repository is public or Render has access

### Connection Timeout
- Check MongoDB Atlas IP whitelist includes Render servers
- Verify MONGODB_URI is correct
- Test connection string locally first

### Frontend Can't Connect to Backend
- Verify VITE_API_URL is correct and includes https://
- Check CORS settings in backend (already configured)
- Ensure backend is running and healthy

### Email Domain Rejection
- Verify email domain is in ALLOWED_DOMAINS
- Check domain spelling matches exactly
- Restart services after updating domains

## Local Testing Before Deployment

```bash
# Test backend
cd backend
cp .env.example .env
# Edit .env with test values
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Test frontend (new terminal)
cd frontend
cp .env.example .env.local
# Edit .env.local
npm install
npm run dev
```

## Rollback Procedure

If deployment has issues:

1. **Render Dashboard**:
   - Go to service > Deploys
   - Click on previous successful deploy
   - Click "Redeploy"

2. **Database**:
   - MongoDB Atlas keeps backups
   - Use backup restore if needed

## Support

For issues:
- Check Render documentation: https://render.com/docs
- Check MongoDB Atlas documentation: https://docs.atlas.mongodb.com
- Check FastAPI docs: https://fastapi.tiangolo.com
- Check React docs: https://react.dev
