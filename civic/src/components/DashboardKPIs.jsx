import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, CircularProgress, Alert } from '@mui/material';
import { 
  Assignment, 
  AssignmentTurnedIn, 
  CheckCircle 
} from '@mui/icons-material';
import StatCard from './StatCard';
import { fetchComplaintStats } from '../api';

const DashboardKPIs = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await fetchComplaintStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to fetch complaint stats:", error);
      setError("Failed to load statistics. Please check if the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>
          Loading statistics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return (
      <Alert severity="warning" sx={{ mb: 3 }}>
        No statistics available.
      </Alert>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" sx={{ mb: 3, fontWeight: 600, color: '#1a1a1a' }}>
        Complaint Statistics
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Total Complaints"
            value={stats.total_complaints}
            icon={Assignment}
            color="#1976D2"
            change={stats.total_complaints > 0 ? 12 : 0}
            changeType="positive"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Active Complaints"
            value={stats.active_complaints}
            icon={AssignmentTurnedIn}
            color="#FF9800"
            change={stats.active_complaints > 0 ? 8 : 0}
            changeType="neutral"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Resolved Today"
            value={stats.resolved_today}
            icon={CheckCircle}
            color="#4CAF50"
            change={stats.resolved_today > 0 ? 15 : 0}
            changeType="positive"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardKPIs;

