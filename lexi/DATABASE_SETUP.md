# Database Setup Guide

This guide will help you install and configure PostgreSQL and Redis for LexiLearn without using Docker.

## 🐘 PostgreSQL Installation

### Windows
1. **Download PostgreSQL**:
   - Visit: https://www.postgresql.org/download/windows/
   - Download the installer for Windows
   - Run the installer as Administrator

2. **Installation Steps**:
   - Choose installation directory
   - Set password for `postgres` user (remember this!)
   - Keep default port (5432)
   - Install all components

3. **Create Database**:
   - Open pgAdmin (comes with PostgreSQL)
   - Connect to server using your password
   - Right-click "Databases" → "Create" → "Database"
   - Name: `lexilearn`
   - Click "Save"

### macOS
1. **Using Homebrew**:
   ```bash
   brew install postgresql
   brew services start postgresql
   ```

2. **Create Database**:
   ```bash
   createdb lexilearn
   ```

### Linux (Ubuntu/Debian)
1. **Install PostgreSQL**:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

2. **Create Database**:
   ```bash
   sudo -u postgres createdb lexilearn
   ```

## 🔴 Redis Installation

### Windows
1. **Download Redis**:
   - Visit: https://github.com/microsoftarchive/redis/releases
   - Download the latest MSI installer
   - Run the installer

2. **Start Redis**:
   - Redis will start automatically as a Windows service
   - Or run: `redis-server`

### macOS
1. **Using Homebrew**:
   ```bash
   brew install redis
   brew services start redis
   ```

### Linux (Ubuntu/Debian)
1. **Install Redis**:
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

## 🔧 Configuration

### Update Environment Variables

The `backend/.env` file should already have the correct settings:

```env
DATABASE_URL=postgresql://lexilearn_user:lexilearn_password@localhost:5432/lexilearn
REDIS_URL=redis://localhost:6379
```

### For PostgreSQL, you may need to:

1. **Create a user** (if using default postgres user):
   ```sql
   -- Connect to PostgreSQL as postgres user
   CREATE USER lexilearn_user WITH PASSWORD 'lexilearn_password';
   GRANT ALL PRIVILEGES ON DATABASE lexilearn TO lexilearn_user;
   ```

2. **Or update the connection string** to use your postgres user:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/lexilearn
   ```

## ✅ Verification

### Test PostgreSQL Connection
```bash
# Windows (if psql is in PATH)
psql -h localhost -U postgres -d lexilearn

# macOS/Linux
psql -h localhost -U postgres -d lexilearn
```

### Test Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

## 🚀 Next Steps

1. **Start the backend server**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🆘 Troubleshooting

### PostgreSQL Issues
- **Connection refused**: Make sure PostgreSQL service is running
- **Authentication failed**: Check username/password in connection string
- **Database doesn't exist**: Create the `lexilearn` database

### Redis Issues
- **Connection refused**: Make sure Redis service is running
- **Command not found**: Install Redis or add to PATH

### Common Commands
```bash
# Start PostgreSQL (Windows)
net start postgresql-x64-15

# Start Redis (Windows)
net start redis

# Check if services are running
netstat -an | findstr :5432  # PostgreSQL
netstat -an | findstr :6379  # Redis
```
