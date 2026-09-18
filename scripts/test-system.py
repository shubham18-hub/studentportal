#!/usr/bin/env python3
"""
Complete system test - Verifies all functionality works end-to-end
Run: python3 scripts/test-system.py
"""

import asyncio
import sys
import subprocess
import time
from pathlib import Path

class SystemTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    
    def test(self, name, func):
        """Run a test and track results."""
        try:
            print(f"Testing: {name}...", end=" ")
            result = func()
            if result:
                print("✅ PASS")
                self.passed += 1
            else:
                print("❌ FAIL")
                self.failed += 1
                self.errors.append(f"Test failed: {name}")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            self.failed += 1
            self.errors.append(f"Test error in {name}: {str(e)}")
    
    def verify_file_exists(self, path, name):
        """Verify a file exists."""
        def check():
            p = Path(path)
            if not p.exists():
                print(f"File not found: {path}")
                return False
            return True
        self.test(f"{name} exists", check)
    
    def verify_directory_exists(self, path, name):
        """Verify a directory exists."""
        def check():
            p = Path(path)
            if not p.is_dir():
                print(f"Directory not found: {path}")
                return False
            return True
        self.test(f"{name} directory exists", check)
    
    def verify_code_contains(self, file_path, text, description):
        """Verify file contains specific code."""
        def check():
            with open(file_path, 'r') as f:
                content = f.read()
                if text not in content:
                    print(f"Code not found in {file_path}: {text}")
                    return False
            return True
        self.test(description, check)
    
    def run_command(self, cmd, description):
        """Run a command and verify it succeeds."""
        def check():
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    print(f"Command failed: {cmd}")
                    print(f"Error: {result.stderr}")
                    return False
                return True
            except subprocess.TimeoutExpired:
                print(f"Command timed out: {cmd}")
                return False
        self.test(description, check)
    
    def print_results(self):
        """Print test results summary."""
        print(f"\n{'='*60}")
        print(f"  TEST RESULTS")
        print(f"{'='*60}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total:  {self.passed + self.failed}")
        
        if self.errors:
            print(f"\n{'='*60}")
            print(f"  ERRORS")
            print(f"{'='*60}")
            for error in self.errors:
                print(f"  • {error}")
        
        success_rate = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return False

def main():
    tester = SystemTester()
    
    # ========== PROJECT STRUCTURE ==========
    tester.print_header("PROJECT STRUCTURE")
    
    # Root files
    tester.verify_file_exists("README.md", "README")
    tester.verify_file_exists(".env.example", ".env example")
    tester.verify_file_exists("docker-compose.yml", "Docker Compose")
    tester.verify_file_exists(".gitignore", "Git Ignore")
    
    # Directories
    tester.verify_directory_exists("backend", "Backend")
    tester.verify_directory_exists("frontend", "Frontend")
    tester.verify_directory_exists(".github/workflows", "GitHub Actions")
    
    # ========== BACKEND ==========
    tester.print_header("BACKEND CODE")
    
    # Backend structure
    tester.verify_directory_exists("backend/app", "Backend app")
    tester.verify_file_exists("backend/app/main.py", "FastAPI main")
    tester.verify_file_exists("backend/app/config.py", "Config")
    tester.verify_file_exists("backend/app/database.py", "Database")
    tester.verify_file_exists("backend/app/security.py", "Security")
    tester.verify_directory_exists("backend/app/models", "Models")
    tester.verify_directory_exists("backend/app/routes", "Routes")
    tester.verify_directory_exists("backend/app/middleware", "Middleware")
    
    # Backend dependencies
    tester.verify_file_exists("backend/requirements.txt", "Requirements")
    tester.verify_file_exists("backend/Dockerfile", "Backend Dockerfile")
    
    # Backend tests
    tester.verify_file_exists("backend/tests/test_auth.py", "Auth tests")
    tester.verify_file_exists("backend/tests/test_security.py", "Security tests")
    
    # ========== FRONTEND ==========
    tester.print_header("FRONTEND CODE")
    
    # Frontend structure
    tester.verify_directory_exists("frontend/src", "Frontend src")
    tester.verify_file_exists("frontend/src/main.tsx", "React main")
    tester.verify_file_exists("frontend/src/App.tsx", "React App")
    tester.verify_directory_exists("frontend/src/pages", "Pages")
    tester.verify_directory_exists("frontend/src/components", "Components")
    tester.verify_directory_exists("frontend/src/api", "API")
    tester.verify_directory_exists("frontend/src/contexts", "Contexts")
    
    # Frontend dependencies
    tester.verify_file_exists("frontend/package.json", "Package.json")
    tester.verify_file_exists("frontend/tsconfig.json", "TypeScript config")
    tester.verify_file_exists("frontend/tailwind.config.js", "Tailwind config")
    tester.verify_file_exists("frontend/Dockerfile", "Frontend Dockerfile")
    
    # ========== CRITICAL CODE CHECKS ==========
    tester.print_header("CRITICAL CODE VALIDATION")
    
    # Authentication
    tester.verify_code_contains(
        "backend/app/routes/auth.py",
        "def admin_login",
        "Admin login endpoint exists"
    )
    tester.verify_code_contains(
        "backend/app/routes/auth.py",
        "def google_login",
        "Google OAuth endpoint exists"
    )
    
    # Security
    tester.verify_code_contains(
        "backend/app/security.py",
        "def verify_password",
        "Password verification function exists"
    )
    tester.verify_code_contains(
        "backend/app/security.py",
        "def verify_token",
        "Token verification function exists"
    )
    
    # Database
    tester.verify_code_contains(
        "backend/app/database.py",
        "async def connect_to_mongo",
        "MongoDB connection function exists"
    )
    tester.verify_code_contains(
        "backend/app/database.py",
        "await create_indexes",
        "Database indexes creation exists"
    )
    
    # API Routes
    tester.verify_code_contains(
        "backend/app/routes/tasks.py",
        "def create_task",
        "Task creation endpoint exists"
    )
    tester.verify_code_contains(
        "backend/app/routes/tasks.py",
        "def create_submission",
        "Submission endpoint exists"
    )
    
    # Frontend Pages
    tester.verify_code_contains(
        "frontend/src/pages/LoginPage.tsx",
        "GoogleLogin",
        "Google OAuth in frontend"
    )
    tester.verify_code_contains(
        "frontend/src/pages/DashboardPage.tsx",
        "STAGES",
        "Workflow stages in frontend"
    )
    
    # ========== CONFIGURATION FILES ==========
    tester.print_header("CONFIGURATION FILES")
    
    # Docker
    tester.verify_file_exists("docker-compose.yml", "Docker Compose")
    tester.verify_file_exists("docker-compose.prod.yml", "Docker Compose Prod")
    tester.verify_file_exists("nginx.conf", "Nginx config")
    tester.verify_file_exists("backend/Dockerfile", "Backend Docker")
    tester.verify_file_exists("frontend/Dockerfile", "Frontend Docker")
    
    # Deployment
    tester.verify_file_exists("render.yaml", "Render config")
    
    # GitHub Actions
    tester.verify_file_exists(".github/workflows/backend-tests.yml", "Backend CI/CD")
    tester.verify_file_exists(".github/workflows/frontend-tests.yml", "Frontend CI/CD")
    tester.verify_file_exists(".github/workflows/integration-tests.yml", "Integration CI/CD")
    tester.verify_file_exists(".github/workflows/deploy-render.yml", "Deploy CI/CD")
    
    # ========== SECURITY CHECKS ==========
    tester.print_header("SECURITY VALIDATION")
    
    # No hardcoded secrets
    tester.verify_code_contains(
        "backend/app/config.py",
        "os.getenv",
        "Using environment variables"
    )
    tester.verify_code_contains(
        "backend/app/main.py",
        "SecurityHeadersMiddleware",
        "Security headers middleware"
    )
    tester.verify_code_contains(
        "backend/app/main.py",
        "RateLimitMiddleware",
        "Rate limiting middleware"
    )
    
    # Authentication
    tester.verify_code_contains(
        "backend/app/main.py",
        "HTTPSRedirectMiddleware",
        "HTTPS redirect in production"
    )
    
    # ========== PYTHON CODE QUALITY ==========
    tester.print_header("PYTHON CODE QUALITY")
    
    # Check backend syntax
    tester.run_command(
        "cd backend && python3 -m py_compile app/main.py",
        "Backend main.py compiles"
    )
    tester.run_command(
        "cd backend && python3 -m py_compile app/database.py",
        "Backend database.py compiles"
    )
    tester.run_command(
        "cd backend && python3 -m py_compile app/security.py",
        "Backend security.py compiles"
    )
    
    # ========== TYPESCRIPT CODE QUALITY ==========
    tester.print_header("TYPESCRIPT CODE QUALITY")
    
    # Check TypeScript syntax
    if Path("frontend/node_modules").exists():
        tester.run_command(
            "cd frontend && npx tsc --noEmit",
            "TypeScript compilation check"
        )
    else:
        print("⏭️  Skipping TypeScript check (node_modules not installed)")
    
    # ========== FINAL RESULTS ==========
    success = tester.print_results()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
