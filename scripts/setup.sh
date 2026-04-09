#!/bin/bash

# CareRemind Setup Script
# Automates the setup process for local development

set -e  # Exit on error

echo "🚀 CareRemind Setup Script"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "📦 Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found (optional for frontend)${NC}"
else
    echo -e "${GREEN}✅ Node.js found${NC}"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker not found (optional)${NC}"
else
    echo -e "${GREEN}✅ Docker found${NC}"
fi

echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your credentials${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd services/fastapi
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate || . venv/Scripts/activate  # Windows compatibility

pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head
echo -e "${GREEN}✅ Database migrations complete${NC}"
echo ""

# Seed database
echo "🌱 Seeding database with demo data..."
python -m scripts.seed_db
echo -e "${GREEN}✅ Database seeded${NC}"
echo ""

# Install frontend dependencies (optional)
cd ../../frontend
if command -v npm &> /dev/null; then
    echo "📦 Installing frontend dependencies..."
    npm install
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping frontend setup (npm not found)${NC}"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo ""
echo "Backend:"
echo "  cd services/fastapi"
echo "  source venv/bin/activate  # or . venv/Scripts/activate on Windows"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Scheduler (separate terminal):"
echo "  cd services/fastapi"
echo "  source venv/bin/activate"
echo "  python -m app.scheduler.main"
echo ""
echo "Frontend (separate terminal):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "🔑 Demo Credentials:"
echo "  Email: demo@careremind.com"
echo "  Password: Demo@123"
echo ""

