# PostgreSQL Migration Guide for LexiLearn

## Overview
This guide will help you migrate your LexiLearn application from SQLite to PostgreSQL for production use. PostgreSQL offers better scalability, performance, and concurrent access capabilities.

## Prerequisites

### 1. Install PostgreSQL
**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run the installer and set a password for the postgres user
- Default port: 5432

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. Create Database
```bash
# Access PostgreSQL CLI
psql -U postgres

# Create database and user
CREATE DATABASE lexilearn;
CREATE USER lexi_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE lexilearn TO lexi_user;

# Exit
\q
```

### 3. Install Python Dependencies
```bash
cd lexi/lexi/backend
pip install -r requirements.txt
```

## Migration Steps

### Step 1: Backup Current Data
Before migrating, backup your SQLite database:
```bash
# Copy the current database
cp lexi.db lexi_backup_$(date +%Y%m%d).db
```

### Step 2: Configure PostgreSQL Connection
Edit `backend/.env` (or create it if it doesn't exist):
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://lexi_user:your_secure_password@localhost:5432/lexilearn

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=lexi_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=lexilearn

# Keep other settings
SECRET_KEY=your-secret-key-change-in-production
OPENAI_API_KEY=your-openai-key
```

### Step 3: Run Migration Script
```bash
cd lexi/lexi/backend
python migrate_to_postgresql.py
```

Expected output:
```
🚀 Starting PostgreSQL migration...
✅ Connected to both databases
✅ PostgreSQL schema created successfully
✅ Migrated 15 users
✅ Migrated 5 lessons
✅ Migrated 150 progress entries
✅ Migrated 8 dyslexia tests
✅ PostgreSQL sequences reset

🎉 Migration completed! Total records migrated: 178

Next steps:
1. Update .env file: DATABASE_TYPE=postgresql
2. Update .env file: DATABASE_URL=postgresql://...
3. Restart the application
```

### Step 4: Verify Migration
```bash
# Connect to PostgreSQL
psql -U lexi_user -d lexilearn

# Check tables
\dt

# Check user count
SELECT COUNT(*) FROM users;

# Check progress entries
SELECT COUNT(*) FROM progress;

# Exit
\q
```

### Step 5: Update Application Config
After migration, update `config.py` to use PostgreSQL by default:
```python
# In backend/config.py
DATABASE_TYPE: str = "postgresql"  # Changed from "sqlite"
DATABASE_URL: str = "postgresql://lexi_user:your_secure_password@localhost:5432/lexilearn"
```

### Step 6: Restart Application
```bash
# Stop current application
# Kill any running Python processes

# Start application with PostgreSQL
cd lexi/lexi/backend
python main.py
```

## Verification

### Test Database Connection
The application should now connect to PostgreSQL. Check logs for:
```
[INFO] Database connected successfully to PostgreSQL
[INFO] Using PostgreSQL database: lexilearn
```

### Test User Registration
1. Navigate to registration page
2. Create a new user account
3. Verify in PostgreSQL:
```bash
psql -U lexi_user -d lexilearn
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;
```

### Test Chat Functionality
1. Login to the application
2. Send a chat message
3. Verify in database:
```bash
SELECT COUNT(*) FROM chat_sessions;
```

## Rollback Procedure

If you need to rollback to SQLite:

### Step 1: Stop Application
```bash
# Kill any running processes
```

### Step 2: Update Config
```python
# In backend/config.py
DATABASE_TYPE: str = "sqlite"
DATABASE_URL: str = "sqlite:///lexi.db"
```

### Step 3: Restore SQLite Database
```bash
cp lexi_backup_YYYYMMDD.db lexi.db
```

### Step 4: Restart Application
```bash
python main.py
```

## Performance Tuning

### PostgreSQL Settings for Production
Edit `postgresql.conf`:
```conf
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB

# Connection settings
max_connections = 100

# Logging
log_destination = 'stderr'
logging_collector = on
log_statement = 'mod'
log_min_duration_statement = 1000
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Connection Pooling
For better performance, consider using PgBouncer:
```bash
# Install PgBouncer
sudo apt install pgbouncer

# Configure in /etc/pgbouncer/pgbouncer.ini
```

## Security Best Practices

### 1. Strong Passwords
```sql
-- Change password
ALTER USER lexi_user WITH PASSWORD 'very_strong_password_here';
```

### 2. Limit Connections
```sql
-- Revoke public schema access
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO lexi_user;
```

### 3. Enable SSL
Edit `postgresql.conf`:
```conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

### 4. Firewall Rules
```bash
# Only allow local connections
sudo ufw allow from 127.0.0.1 to any port 5432
```

## Monitoring

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('lexilearn'));
```

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Active Connections
```sql
SELECT 
    pid, 
    usename, 
    application_name, 
    client_addr, 
    state
FROM pg_stat_activity
WHERE datname = 'lexilearn';
```

### Performance Monitoring
```sql
-- Check slow queries
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

**2. Authentication Failed**
- Verify username and password in `.env`
- Check `pg_hba.conf` for authentication method

**3. Permission Denied**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE lexilearn TO lexi_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lexi_user;
```

**4. Migration Errors**
- Check PostgreSQL logs: `/var/log/postgresql/`
- Verify database exists: `psql -l`
- Check user permissions

## Next Steps

1. **Backup Strategy**: Set up automated backups
   ```bash
   # Daily backup script
   pg_dump -U lexi_user lexilearn > backup_$(date +%Y%m%d).sql
   ```

2. **Monitoring**: Implement database monitoring tool
3. **Scaling**: Consider connection pooling and read replicas
4. **SSL**: Enable SSL for secure connections
5. **Performance**: Use `EXPLAIN ANALYZE` to optimize queries

## Support

For issues or questions:
1. Check PostgreSQL logs
2. Review application logs
3. Consult PostgreSQL documentation
4. Review migration script output

## Summary

✅ **Completed Tasks:**
- [x] PostgreSQL configuration added
- [x] Migration script created
- [x] Dependencies updated
- [x] Natural conversation enhancements implemented
- [x] Conversation memory and context tracking added

✅ **Ready for Production:**
- PostgreSQL support is production-ready
- Migration script is tested
- Enhanced AI chat with natural conversation flow
- Context-aware responses implemented

📝 **Next Steps for Production:**
1. Run migration script on production database
2. Update environment variables
3. Restart application
4. Monitor performance
5. Set up backups
