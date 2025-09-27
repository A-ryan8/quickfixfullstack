const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Database connection
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'civic_complaints'
};

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Civic Complaint Management API - Node.js Version' });
});

app.get('/api/complaints', async (req, res) => {
  try {
    const connection = await mysql.createConnection(dbConfig);
    const [rows] = await connection.execute('SELECT * FROM complaints ORDER BY created_at DESC');
    await connection.end();
    
    res.json(rows);
  } catch (error) {
    console.error('Error fetching complaints:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/api/complaints', async (req, res) => {
  try {
    const { title, description, location, status = 'pending' } = req.body;
    
    const connection = await mysql.createConnection(dbConfig);
    const [result] = await connection.execute(
      'INSERT INTO complaints (title, description, location, status) VALUES (?, ?, ?, ?)',
      [title, description, location, status]
    );
    await connection.end();
    
    res.json({ 
      id: result.insertId, 
      title, 
      description, 
      location, 
      status,
      message: 'Complaint created successfully' 
    });
  } catch (error) {
    console.error('Error creating complaint:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/complaints/stats', async (req, res) => {
  try {
    const connection = await mysql.createConnection(dbConfig);
    
    const [totalResult] = await connection.execute('SELECT COUNT(*) as total FROM complaints');
    const [pendingResult] = await connection.execute('SELECT COUNT(*) as pending FROM complaints WHERE status = "pending"');
    const [resolvedResult] = await connection.execute('SELECT COUNT(*) as resolved FROM complaints WHERE status = "resolved"');
    
    await connection.end();
    
    res.json({
      total_complaints: totalResult[0].total,
      pending_complaints: pendingResult[0].pending,
      resolved_complaints: resolvedResult[0].resolved
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Database: ${dbConfig.database}@${dbConfig.host}`);
});
