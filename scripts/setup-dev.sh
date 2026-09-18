#!/bin/bash

# E-Cell Portal Development Setup Script
# This script sets up the development environment

set -e

echo "================================================"
echo "E-Cell Portal - Development Setup"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${BLUE}Please edit .env with your credentials${NC}"
fi

# Backend setup
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

if [ ! -d venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null

if [ ! -f .env ]; then
    cp .env.example .env
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

cd ..

# Frontend setup
echo -e "${BLUE}Setting up frontend...${NC}"
cd frontend

if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo -e "${BLUE}Please edit frontend/.env.local with your credentials${NC}"
fi

echo "Installing Node dependencies..."
npm install

cd ..

echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with MongoDB and OAuth credentials"
echo "2. Edit frontend/.env.local with API URL and Google Client ID"
echo "3. Run 'npm run dev:backend' in one terminal"
echo "4. Run 'npm run dev:frontend' in another terminal"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
