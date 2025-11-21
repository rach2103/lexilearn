# Lexi - Dyslexia Learning Platform Setup Guide

## Prerequisites

### Required Software
- **Node.js**: Version 18.18.0 or higher
- **Python**: Version 3.8 or higher
- **Git**: Latest version

### Installation Links
- Node.js: https://nodejs.org/en/download/
- Python: https://www.python.org/downloads/
- Git: https://git-scm.com/downloads

## Quick Setup Steps

### 1. Install Node.js (if not installed)
```bash
# Check if Node.js is installed
node --version
npm --version

# If not installed, download from nodejs.org
# Recommended: Use Node Version Manager (nvm)
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env file with your configurations

# Run database setup
python -c "from database.database import DatabaseManager; DatabaseManager()"

# Start backend server
python main.py
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

## Detailed Setup Instructions

### Backend Configuration

1. **Environment Variables** (backend/.env):
```env
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///lexi.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
DEBUG=True
```

2. **Database Setup**:
   - SQLite (default): No additional setup required
   - PostgreSQL: Install PostgreSQL and update DATABASE_URL
   - MongoDB: Install MongoDB and update configuration

### Frontend Configuration

1. **Environment Variables** (frontend/.env):
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

2. **Node.js Version**:
   - Use Node.js 18.18.0 (specified in .nvmrc)
   - If using nvm: `nvm use`

## Running the Application

### Development Mode

1. **Start Backend** (Terminal 1):
```bash
cd backend
venv\Scripts\activate  # Windows
python main.py
```

2. **Start Frontend** (Terminal 2):
```bash
cd frontend
npm start
```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Production Build

1. **Build Frontend**:
```bash
cd frontend
npm run build
```

2. **Deploy Backend**:
```bash
cd backend
pip install gunicorn
gunicorn main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues

1. **Node.js Version Conflicts**:
```bash
# Use nvm to manage Node versions
nvm install 18.18.0
nvm use 18.18.0
```

2. **Port Already in Use**:
```bash
# Kill process on port 3000 (frontend)
npx kill-port 3000

# Kill process on port 8000 (backend)
npx kill-port 8000
```

3. **Python Virtual Environment Issues**:
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

4. **npm Install Failures**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Performance Optimization

1. **Frontend**:
   - Use `npm run build` for production
   - Enable service worker for caching
   - Optimize images and assets

2. **Backend**:
   - Use PostgreSQL for production
   - Implement Redis for caching
   - Configure proper logging

## Development Workflow

1. **Code Changes**:
   - Frontend: Hot reload enabled (automatic refresh)
   - Backend: Manual restart required

2. **Testing**:
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
python -m pytest
```

3. **Linting**:
```bash
# Frontend
npm run lint

# Backend
flake8 .
black .
```

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **React Documentation**: https://reactjs.org/docs
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Tailwind CSS**: https://tailwindcss.com/docs