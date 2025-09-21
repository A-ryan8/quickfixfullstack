import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

const StatCard = ({ 
  title, 
  value, 
  change, 
  changeType = 'neutral', // 'positive', 'negative', 'neutral'
  icon: Icon,
  color = '#1976D2'
}) => {
  const getTrendIcon = () => {
    switch (changeType) {
      case 'positive':
        return <TrendingUp sx={{ color: '#4caf50', fontSize: 16 }} />;
      case 'negative':
        return <TrendingDown sx={{ color: '#f44336', fontSize: 16 }} />;
      default:
        return <TrendingFlat sx={{ color: '#757575', fontSize: 16 }} />;
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return '#4caf50';
      case 'negative':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${color}15 0%, ${color}05 100%)`,
        border: `1px solid ${color}30`,
        borderRadius: 2,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 25px ${color}25`,
        }
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              backgroundColor: `${color}20`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            {Icon && <Icon sx={{ color: color, fontSize: 24 }} />}
          </Box>
          {change !== undefined && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {getTrendIcon()}
              <Typography 
                variant="body2" 
                sx={{ 
                  color: getChangeColor(),
                  fontWeight: 600,
                  fontSize: '0.875rem'
                }}
              >
                {change > 0 ? '+' : ''}{change}%
              </Typography>
            </Box>
          )}
        </Box>
        
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: 700, 
            color: '#1a1a1a',
            mb: 0.5,
            lineHeight: 1.2
          }}
        >
          {value}
        </Typography>
        
        <Typography 
          variant="body2" 
          sx={{ 
            color: '#666',
            fontWeight: 500,
            fontSize: '0.875rem'
          }}
        >
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default StatCard;

