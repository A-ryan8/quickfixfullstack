import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

const Messages = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://10.30.243.189:3000/api/messages');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessages(data);
    } catch (err) {
      console.error('Error fetching messages:', err);
      setError('Failed to fetch messages. Make sure the backend server is running on localhost:3000');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
    
    // Set up polling to refresh messages every 5 seconds
    const interval = setInterval(fetchMessages, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading && messages.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Messages from Flutter App
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="body2" color="text.secondary">
            Auto-refreshing every 5 seconds
          </Typography>
          <RefreshIcon 
            onClick={fetchMessages} 
            sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}
          />
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {messages.length === 0 && !loading ? (
        <Card>
          <CardContent>
            <Typography variant="h6" color="text.secondary" textAlign="center">
              No messages yet. Send a message from the Flutter app to see it here!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {messages.map((message, index) => (
            <Card key={index} sx={{ maxWidth: '100%' }}>
              <CardContent>
                <Typography variant="body1" paragraph>
                  {message.text}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Received: {formatTimestamp(message.timestamp)}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {loading && messages.length > 0 && (
        <Box display="flex" justifyContent="center" mt={2}>
          <CircularProgress size={24} />
        </Box>
      )}
    </Box>
  );
};

export default Messages;
