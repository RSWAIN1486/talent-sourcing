import { Box, Card, CardContent, Grid, Typography, CircularProgress, useTheme } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { jobsApi } from '../services/api';
import WorkIcon from '@mui/icons-material/Work';
import PeopleIcon from '@mui/icons-material/People';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PhoneIcon from '@mui/icons-material/Phone';

export default function Statistics() {
  const theme = useTheme();

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['jobStats'],
    queryFn: jobsApi.getJobStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Typography color="error">Error loading statistics</Typography>
      </Box>
    );
  }

  const statCards = [
    {
      title: 'Total Jobs',
      value: stats?.total_jobs || 0,
      icon: WorkIcon,
      color: theme.palette.primary.main,
      bgGradient: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.2) 100%)'
    },
    {
      title: 'Total Candidates',
      value: stats?.total_candidates || 0,
      icon: PeopleIcon,
      color: theme.palette.success.main,
      bgGradient: 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.2) 100%)'
    },
    {
      title: 'Resume Screened',
      value: stats?.resume_screened || 0,
      icon: AssignmentIcon,
      color: theme.palette.warning.main,
      bgGradient: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.2) 100%)'
    },
    {
      title: 'Phone Screened',
      value: stats?.phone_screened || 0,
      icon: PhoneIcon,
      color: theme.palette.error.main,
      bgGradient: 'linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.2) 100%)'
    }
  ];

  return (
    <Box 
      sx={{ 
        p: { xs: 2, sm: 3, md: 4 },
        minHeight: '100vh',
        bgcolor: theme.palette.mode === 'dark' ? 'background.default' : 'grey.50'
      }}
    >
      <Typography 
        variant="h4" 
        gutterBottom 
        sx={{ 
          mb: 4,
          fontWeight: 600,
          color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main',
        }}
      >
        Statistics
      </Typography>
      
      <Grid container spacing={3}>
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Grid item xs={12} sm={6} md={3} key={stat.title}>
              <Card 
                elevation={0}
                sx={{ 
                  height: '100%',
                  background: theme.palette.mode === 'dark' 
                    ? 'rgba(255, 255, 255, 0.05)' 
                    : stat.bgGradient,
                  borderRadius: 2,
                  transition: 'transform 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.shadows[4]
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" alignItems="center" mb={3}>
                    <Icon 
                      sx={{ 
                        fontSize: 40, 
                        color: stat.color,
                        mr: 2,
                        transition: 'transform 0.2s ease-in-out',
                        '&:hover': {
                          transform: 'scale(1.1)'
                        }
                      }} 
                    />
                    <Typography 
                      variant="h6" 
                      component="div"
                      sx={{ 
                        fontWeight: 500,
                        color: theme.palette.mode === 'dark' ? 'text.primary' : 'text.primary'
                      }}
                    >
                      {stat.title}
                    </Typography>
                  </Box>
                  <Typography 
                    variant="h3" 
                    component="div" 
                    sx={{ 
                      textAlign: 'center',
                      fontWeight: 600,
                      color: stat.color,
                      transition: 'color 0.2s ease-in-out'
                    }}
                  >
                    {stat.value.toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
} 