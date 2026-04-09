@echo off
REM CareRemind Setup Script for Windows

echo.
echo 🚀 CareRemind Setup Script
echo ==========================
echo.

REM Check if Python is installed
echo 📦 Checking dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed
    exit /b 1
)
echo ✅ Python found
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created
    echo ⚠️  Please edit .env and add your credentials
) else (
    echo ✅ .env file already exists
)
echo.

REM Install backend dependencies
echo 📦 Installing backend dependencies...
cd services\fastapi
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Backend dependencies installed
echo.

REM Run database migrations
echo 🗄️  Running database migrations...
alembic upgrade head
echo ✅ Database migrations complete
echo.

REM Seed database
echo 🌱 Seeding database with demo data...
python -m scripts.seed_db
echo ✅ Database seeded
echo.

REM Install frontend dependencies
cd ..\..\frontend
where npm >nul 2>&1
if not errorlevel 1 (
    echo 📦 Installing frontend dependencies...
    call npm install
    echo ✅ Frontend dependencies installed
) else (
    echo ⚠️  Skipping frontend setup (npm not found)
)

cd ..

echo.
echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo.
echo Backend:
echo   cd services\fastapi
echo   venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload
echo.
echo Scheduler (separate terminal):
echo   cd services\fastapi
echo   venv\Scripts\activate.bat
echo   python -m app.scheduler.main
echo.
echo Frontend (separate terminal):
echo   cd frontend
echo   npm run dev
echo.
echo 📚 API Documentation: http://localhost:8000/docs
echo 🎨 Frontend: http://localhost:3000
echo.
echo 🔑 Demo Credentials:
echo   Email: demo@careremind.com
echo   Password: Demo@123
echo.

