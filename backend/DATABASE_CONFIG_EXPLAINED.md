# Database Configuration Explained

## Overview
This document explains the database configuration for the Civic Complaint Management API.

## Database Schema

### Complaints Table
```sql
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    status ENUM('pending', 'in_progress', 'resolved') DEFAULT 'pending',
    priority_score FLOAT DEFAULT 0.0,
    upvote_count INT DEFAULT 0,
    image_url VARCHAR(500),
    pdf_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Upvotes Table
```sql
CREATE TABLE upvotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_complaint (complaint_id, user_id)
);
```

## Environment Variables

### Database Configuration
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=civic_complaints
```

### Connection Pool Settings
```python
# Database connection pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Database Setup

### 1. Create Database
```sql
CREATE DATABASE civic_complaints;
```

### 2. Create Tables
```sql
-- Run the schema files in order:
-- 1. complaints_table.sql
-- 2. upvotes_table.sql
-- 3. indexes.sql
```

### 3. Insert Sample Data
```sql
INSERT INTO complaints (title, description, location, status) VALUES
('Pothole on Main Street', 'Large pothole causing traffic issues', 'Main Street, Downtown', 'pending'),
('Broken Streetlight', 'Streetlight not working at night', 'Oak Avenue, Residential', 'in_progress'),
('Garbage Collection Issue', 'Garbage not collected for 3 days', 'Pine Street, Commercial', 'resolved');
```

## Connection Management

### Connection Pool
- **Pool Size**: 10 connections
- **Max Overflow**: 20 additional connections
- **Pre-ping**: Enabled to check connection health
- **Recycle**: Connections recycled every hour

### Session Management
```python
# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Performance Optimization

### Indexes
```sql
-- Index on status for filtering
CREATE INDEX idx_complaints_status ON complaints(status);

-- Index on priority_score for sorting
CREATE INDEX idx_complaints_priority ON complaints(priority_score DESC);

-- Index on created_at for time-based queries
CREATE INDEX idx_complaints_created_at ON complaints(created_at);

-- Composite index for upvotes
CREATE INDEX idx_upvotes_complaint_user ON upvotes(complaint_id, user_id);
```

### Query Optimization
- Use `LIMIT` and `OFFSET` for pagination
- Use `ORDER BY` with indexed columns
- Use `WHERE` clauses with indexed columns
- Avoid `SELECT *` - specify required columns

## Backup and Recovery

### Backup
```bash
mysqldump -u root -p civic_complaints > backup.sql
```

### Restore
```bash
mysql -u root -p civic_complaints < backup.sql
```

## Monitoring

### Connection Monitoring
```python
# Check connection pool status
engine.pool.status()
```

### Query Performance
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## Troubleshooting

### Common Issues
1. **Connection Timeout**: Increase `pool_recycle` value
2. **Too Many Connections**: Reduce `pool_size` or increase `max_overflow`
3. **Slow Queries**: Add appropriate indexes
4. **Memory Issues**: Optimize query results with `LIMIT`

### Health Checks
```python
# Test database connection
def test_connection():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
```
