# E-Cell Task/Submission Portal

A full-stack task management and submission portal for E-Cell teams with role-based workflows, PDF submissions, and grading.

## Features

- **Role-Based Access**: Admin (email/password), Students & Faculty (Google OAuth restricted to klecba.edu.in, kle.ac.in, klecba.edu domains)
- **Workflow Stages**: Preliminary → Ignite Propel → Comprehensive
- **Task Management**: Admins create and manage tasks with deadlines, points, guidelines
- **PDF Submissions**: Students submit PDFs with status tracking (Not Submitted, Submitted, Graded)
- **Grading System**: Admin grading with points assignment
- **Analytics Dashboard**: Response tracking and performance metrics
- **Theme Support**: Dark/light mode with blue accent colors
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: FastAPI, MongoDB, Python 3.10+
- **Frontend**: React 18+, TypeScript, Tailwind CSS
- **Auth**: Google OAuth 2.0 + JWT
- **Deployment**: Docker, Docker Compose, Render

## Project Structure

```
studentportal/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── models/         # Pydantic models
│   │   ├── routes/         # API endpoints
│   │   ├── middleware/     # Authentication, CORS
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── utils/          # Utilities
│   │   ├── styles/         # Tailwind config
│   │   └── App.tsx
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## 🤖 Automated Testing

Every deployment is **automatically tested** using GitHub Actions:

- ✅ Backend tests (security, API, scalability)
- ✅ Frontend tests (build, audit, security)
- ✅ Integration tests (end-to-end)
- ✅ Security scanning (secrets, vulnerabilities)
- ✅ Performance validation

**See**: [AUTOMATED_TESTING_SUMMARY.md](AUTOMATED_TESTING_SUMMARY.md) for details

Tests run automatically on:
- Push to main/develop
- Pull requests
- Manual workflow trigger

Only tested code is deployed. Deploy with confidence! ✅

---

## Quick Start

### Local Development

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your MongoDB and OAuth credentials
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local with your API endpoint
   npm run dev
   ```

### Docker Compose

```bash
docker-compose up -d
```

Access frontend at `http://localhost:3000` and backend at `http://localhost:8000`.

## Environment Variables

### Backend (.env)
```
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ecell
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
ADMIN_EMAIL=admin@ecell.com
ADMIN_PASSWORD_HASH=hashed-password
ALLOWED_DOMAINS=klecba.edu.in,kle.ac.in,klecba.edu
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

## Deployment

See `Dockerfile`, `docker-compose.yml`, and render deployment configuration files for production setup.

## API Documentation

Once backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## License

MIT
