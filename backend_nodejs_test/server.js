// backend/server.js
import express from 'express';
import cors from 'cors';

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

// In-memory "database"
const messages = [];

// GET endpoint to retrieve all messages
app.get('/api/messages', (req, res) => {
  console.log('GET /api/messages - Sending messages...');
  res.json(messages);
});

// POST endpoint to add a new message
app.post('/api/messages', (req, res) => {
  const { message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Message content is required' });
  }
  const newMessage = {
    text: message,
    timestamp: new Date().toISOString()
  };
  messages.push(newMessage);
  console.log('POST /api/messages - New message added:', newMessage);
  res.status(201).json(newMessage);
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Backend server is running at http://localhost:${port}`);
  console.log(`Also accessible at http://10.30.243.189:${port}`);
});
