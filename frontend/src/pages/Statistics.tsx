import { Box, Card, CardContent, Grid, Typography, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { jobsApi } from '../services/api';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PhoneIcon from '@mui/icons-material/Phone';

export default function Statistics() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['jobStats'],
    queryFn: jobsApi.getJobStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <Typography color="error">Error loading statistics</Typography>
      </Box>
    );
  }

  const statCards = [
    {
      title: 'Total Jobs',
      value: stats?.total_jobs || 0,
      icon: WorkIcon,
      color: '#2196f3' // Blue
    },
    {
      title: 'Total Candidates',
      value: stats?.total_candidates || 0,
      icon: PeopleIcon,
      color: '#4caf50' // Green
    },
    {
      title: 'Resume Screened',
      value: stats?.resume_screened || 0,
      icon: AssignmentIcon,
      color: '#ff9800' // Orange
    },
    {
      title: 'Phone Screened',
      value: stats?.phone_screened || 0,
      icon: PhoneIcon,
      color: '#f44336' // Red
    }
  ];

  return (
    <Box sx={{ pt: 8, px: 3 }}>
      <Typography variant="h4" gutterBottom>Statistics</Typography>
      
      <Grid container spacing={3}>
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={stat.title}>
              <Card 
                sx={{ 
                  height: '100%',
                  '&:hover': {
                    boxShadow: (theme) => theme.shadows[4]
                  }
                }}
              >
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Icon sx={{ fontSize: 40, color: stat.color, mr: 1 }} />
                    <Typography variant="h6" component="div">
                      {stat.title}
                    </Typography>
                  </Box>
                  <Typography variant="h3" component="div" align="center">
                    {stat.value.toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Add more statistics sections here if needed */}
    </Box>
  );
} 