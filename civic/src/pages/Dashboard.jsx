// civic/src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Alert, CircularProgress } from '@mui/material';
import { fetchComplaints, updateComplaintStatus, deleteComplaint } from '../api';
import DashboardKPIs from '../components/DashboardKPIs';
import ComplaintCard from '../components/ComplaintCard';

const Dashboard = () => {
    const [complaints, setComplaints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [updatingStatus, setUpdatingStatus] = useState(new Set());

    const loadComplaints = async () => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await fetchComplaints();
            setComplaints(data);
        } catch (error) {
            console.error("Failed to fetch complaints:", error);
            setError("Failed to load complaints. Please check if the backend server is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadComplaints();
    }, []);

    const handleStatusChange = async (id, newStatus) => {
        // Add to updating set
        setUpdatingStatus(prev => new Set(prev).add(id));
        
        try {
            console.log(`Updating complaint ${id} status to: ${newStatus}`);
            await updateComplaintStatus(id, newStatus);
            console.log(`Successfully updated complaint ${id} status to: ${newStatus}`);
            
            // Refresh the list to show the updated status
            await loadComplaints();
            console.log("Complaints list refreshed successfully");
        } catch (error) {
            console.error("Failed to update status:", error);
            setError(`Failed to update complaint status: ${error.response?.data?.detail || error.message}`);
        } finally {
            // Remove from updating set
            setUpdatingStatus(prev => {
                const newSet = new Set(prev);
                newSet.delete(id);
                return newSet;
            });
        }
    };

    const handleDeleteComplaint = async (id) => {
        try {
            console.log(`🗑️ Deleting complaint ${id}`);
            
            // Check if user is authenticated
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('❌ No authentication token found');
                setError('You must be logged in to delete complaints');
                return;
            }
            
            console.log('🔐 Authentication token found:', token.substring(0, 20) + '...');
            
            await deleteComplaint(id);
            console.log(`✅ Successfully deleted complaint ${id}`);
            
            // Refresh the list to show the updated data
            await loadComplaints();
            console.log("📋 Complaints list refreshed after deletion");
        } catch (error) {
            console.error("❌ Failed to delete complaint:", error);
            console.error("Error details:", error.response?.data);
            setError(`Failed to delete complaint: ${error.response?.data?.detail || error.message}`);
        }
    };


	return (
        <Box sx={{ width: '100%', padding: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" gutterBottom>
                    Civic Complaints Dashboard
                </Typography>
                <Button 
                    variant="outlined" 
                    onClick={loadComplaints}
                    disabled={loading}
                >
                    Refresh
                </Button>
            </Box>
            
            {/* KPI Cards */}
            <DashboardKPIs />
            
            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}
            
            {/* Complaints List - Card Layout */}
            <Box sx={{ mt: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h5" sx={{ fontWeight: 600, color: 'text.primary' }}>
                        Complaints ({complaints.length})
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Click on any card to view the PDF report
                    </Typography>
                </Box>
                
                {loading ? (
                    <Box sx={{ 
                        display: 'flex', 
                        justifyContent: 'center', 
                        alignItems: 'center', 
                        py: 8,
                        flexDirection: 'column',
                        gap: 2
                    }}>
                        <CircularProgress size={40} />
                        <Typography variant="body1" color="text.secondary">
                            Loading complaints...
                        </Typography>
                    </Box>
                ) : complaints.length === 0 ? (
                    <Box sx={{ 
                        textAlign: 'center', 
                        py: 8,
                        backgroundColor: 'grey.50',
                        borderRadius: 3,
                        border: '2px dashed',
                        borderColor: 'grey.300'
                    }}>
                        <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                            No complaints found
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            New complaints will appear here when submitted from the mobile app
                        </Typography>
                    </Box>
                ) : (
                    <Box sx={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        gap: 0,
                        maxWidth: '100%'
                    }}>
                        {complaints.map((complaint) => (
                            <ComplaintCard
                                key={complaint.id}
                                complaint={complaint}
                                onStatusChange={handleStatusChange}
                                onDelete={handleDeleteComplaint}
                            />
                        ))}
                    </Box>
                )}
            </Box>
        </Box>
    );
};

export default Dashboard;