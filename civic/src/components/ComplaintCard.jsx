// civic/src/components/ComplaintCard.jsx
import React, { useState } from 'react';
import { 
    Card, 
    CardActionArea, 
    CardMedia, 
    CardContent, 
    Typography, 
    Grid, 
    Select, 
    MenuItem, 
    Button, 
    Box,
    Chip,
    IconButton,
    Tooltip
} from '@mui/material';
import { 
    LocationOn as LocationOnIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    PictureAsPdf as PdfIcon,
    Image as ImageIcon,
    Delete as DeleteIcon
} from '@mui/icons-material';

const ComplaintCard = ({ complaint, onStatusChange, onDelete }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [imageError, setImageError] = useState(false);
    
    // Function to open the PDF in a new tab
    const handleCardClick = () => {
        if (complaint.pdfUrl) {
            // Fix PDF URL construction - remove leading slash if present
            const pdfPath = complaint.pdfUrl.startsWith('/') ? complaint.pdfUrl.slice(1) : complaint.pdfUrl;
            window.open(`http://localhost:8000/${pdfPath}`, '_blank');
        } else {
            alert('No PDF available for this complaint.');
        }
    };

    // Function to open Google Maps with correct URL format
    const handleLocationClick = (e) => {
        e.stopPropagation();
        const locationString = complaint.location.replace('Lat:', '').replace('Lng:', '');
        const [lat, lng] = locationString.split(',').map(s => s.trim());
        if(lat && lng) {
            // Use the correct Google Maps API format
            window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, '_blank');
        }
    };

    // Function to handle status change and stop event propagation
    const handleStatusSelectChange = (e) => {
        e.stopPropagation();
        onStatusChange(complaint.id, e.target.value);
    };

    // Function to toggle description expansion
    const handleExpandClick = (e) => {
        e.stopPropagation();
        setIsExpanded(!isExpanded);
    };

    // Function to handle image error
    const handleImageError = () => {
        setImageError(true);
    };

    // Function to handle delete button click
    const handleDeleteClick = (e) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this complaint? This action cannot be undone.')) {
            onDelete(complaint.id);
        }
    };

    // Get status color for chip
    const getStatusColor = (status) => {
        switch (status) {
            case 'New': return 'primary';
            case 'In Progress': return 'warning';
            case 'Resolved': return 'success';
            case 'Closed': return 'default';
            default: return 'primary';
        }
    };

    // Truncate description for display
    const shouldTruncate = complaint.description.length > 150;
    const displayDescription = isExpanded || !shouldTruncate 
        ? complaint.description 
        : complaint.description.substring(0, 150) + '...';

    // Fix image URL construction - remove leading slash if present
    const imagePath = complaint.imageUrl && complaint.imageUrl.startsWith('/') 
        ? complaint.imageUrl.slice(1) 
        : complaint.imageUrl;

    return (
        <Card 
            sx={{ 
                display: 'flex', 
                mb: 3, 
                boxShadow: 4,
                borderRadius: 3,
                overflow: 'hidden',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                    boxShadow: 6,
                    transform: 'translateY(-2px)'
                }
            }}
        >
            <CardActionArea 
                onClick={handleCardClick} 
                sx={{ 
                    display: 'flex', 
                    p: 0,
                    '&:hover': {
                        backgroundColor: 'rgba(0, 0, 0, 0.02)'
                    }
                }}
            >
                {/* Image Section */}
                <Box sx={{ position: 'relative', minWidth: 200, height: 200 }}>
                    {complaint.imageUrl && !imageError ? (
                        <CardMedia
                            component="img"
                            sx={{ 
                                width: '100%', 
                                height: '100%', 
                                objectFit: 'cover'
                            }}
                            image={`http://localhost:8000/${imagePath}`}
                            alt="Complaint Image"
                            onError={handleImageError}
                        />
                    ) : (
                        <Box 
                            sx={{ 
                                width: '100%', 
                                height: '100%', 
                                display: 'flex', 
                                alignItems: 'center', 
                                justifyContent: 'center',
                                backgroundColor: 'grey.100',
                                flexDirection: 'column',
                                gap: 1
                            }}
                        >
                            <ImageIcon sx={{ fontSize: 40, color: 'grey.400' }} />
                            <Typography variant="caption" color="text.secondary">
                                No Image
                            </Typography>
                        </Box>
                    )}
                    
                    {/* PDF Indicator */}
                    {complaint.pdfUrl && (
                        <Tooltip title="Click to view PDF report">
                            <Box
                                sx={{
                                    position: 'absolute',
                                    top: 8,
                                    right: 8,
                                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                                    borderRadius: '50%',
                                    p: 0.5,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}
                            >
                                <PdfIcon sx={{ color: 'white', fontSize: 20 }} />
                            </Box>
                        </Tooltip>
                    )}
                </Box>

                {/* Content Section */}
                <Box sx={{ flex: 1, p: 3 }}>
                    <CardContent sx={{ p: 0, '&:last-child': { pb: 0 } }}>
                        {/* Header with Status, Score and Date */}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Submitted: {new Date(complaint.created_at).toLocaleString()}
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                {typeof complaint.priority_score !== 'undefined' && complaint.priority_score !== null && (
                                    <Chip 
                                        label={`Score: ${complaint.priority_score}`}
                                        color="secondary"
                                        size="small"
                                        sx={{ fontWeight: 700 }}
                                    />
                                )}
                                <Chip 
                                    label={complaint.status} 
                                    color={getStatusColor(complaint.status)}
                                    size="small"
                                    sx={{ fontWeight: 600 }}
                                />
                            </Box>
                        </Box>

                        {/* Title */}
                        {complaint.title && (
                            <Typography 
                                variant="h5" 
                                component="div" 
                                sx={{ 
                                    mb: 1, 
                                    color: 'primary.main',
                                    fontWeight: 600
                                }}
                            >
                                {complaint.title}
                            </Typography>
                        )}
                        
                        {/* Description */}
                        <Typography 
                            variant="h6" 
                            component="div" 
                            sx={{ 
                                mb: 2, 
                                lineHeight: 1.4,
                                color: 'text.primary',
                                fontWeight: 500
                            }}
                        >
                            {displayDescription}
                        </Typography>

                        {/* Expand/Collapse Button */}
                        {shouldTruncate && (
                            <Button
                                size="small"
                                onClick={handleExpandClick}
                                endIcon={isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                sx={{ 
                                    mb: 2, 
                                    textTransform: 'none',
                                    color: 'primary.main'
                                }}
                            >
                                {isExpanded ? 'Show Less' : 'Read More'}
                            </Button>
                        )}

                        {/* Action Buttons */}
                        <Grid container spacing={2} alignItems="center">
                            <Grid item>
                                <Button 
                                    size="medium" 
                                    variant="outlined" 
                                    startIcon={<LocationOnIcon />}
                                    onClick={handleLocationClick}
                                    sx={{
                                        borderRadius: 2,
                                        textTransform: 'none',
                                        fontWeight: 500,
                                        px: 2,
                                        py: 1
                                    }}
                                >
                                    View Location
                                </Button>
                            </Grid>
                            <Grid item>
                                <Select
                                    size="medium"
                                    value={complaint.status}
                                    onClick={(e) => e.stopPropagation()}
                                    onChange={handleStatusSelectChange}
                                    sx={{ 
                                        minWidth: 140,
                                        borderRadius: 2,
                                        '& .MuiOutlinedInput-notchedOutline': {
                                            borderColor: 'primary.main'
                                        }
                                    }}
                                >
                                    <MenuItem value="New">New</MenuItem>
                                    <MenuItem value="In Progress">In Progress</MenuItem>
                                    <MenuItem value="Resolved">Resolved</MenuItem>
                                    <MenuItem value="Closed">Closed</MenuItem>
                                </Select>
                            </Grid>
                            <Grid item>
                                <Tooltip title="Delete complaint">
                                    <IconButton
                                        onClick={handleDeleteClick}
                                        sx={{
                                            color: 'error.main',
                                            '&:hover': {
                                                backgroundColor: 'error.light',
                                                color: 'error.dark'
                                            }
                                        }}
                                    >
                                        <DeleteIcon />
                                    </IconButton>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardContent>
                </Box>
            </CardActionArea>
        </Card>
    );
};

export default ComplaintCard;
