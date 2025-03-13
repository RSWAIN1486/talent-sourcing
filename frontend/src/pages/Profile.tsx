import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Divider,
  Grid,
  Button,
  useTheme,
  Tab,
  Tabs,
  CircularProgress,
  Alert
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import PhoneIcon from '@mui/icons-material/Phone';
import { authApi } from '../services/api';
import GlobalVoiceSettings from '../components/voice-agent/GlobalVoiceSettings';
import { AIPoweredBadge } from '../components/AIPoweredBadge';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function Profile() {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['user-profile'],
    queryFn: authApi.getCurrentUser,
    retry: 1,
  });
  if (error) {
    console.error('Profile loading error:', error);
    setErrorDetails(error.message || 'Unknown error');
  }

  useEffect(() => {
    // Log for debugging
    console.log('Profile component mounted');
    console.log('Auth token:', localStorage.getItem('access_token'));
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading profile. Please try again later.
          {errorDetails && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Details: {errorDetails}
            </Typography>
          )}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      width: '100%',
      bgcolor: 'background.default',
      transition: 'background-color 0.3s ease',
      p: { xs: 2, sm: 3, md: 4 }
    }}>
      <Typography 
        variant="h4" 
        gutterBottom 
        sx={{ 
          mb: 4,
          fontWeight: 600,
          color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main',
        }}
      >
        Profile & Settings
      </Typography>

      <Grid container spacing={4}>
        {/* Profile Card */}
        <Grid item xs={12} md={4}>
          <Card 
            sx={{ 
              height: '100%',
              borderRadius: 2,
              bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
              boxShadow: theme.shadows[2]
            }}
          >
            <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Avatar 
                sx={{ 
                  width: 100, 
                  height: 100, 
                  bgcolor: theme.palette.primary.main,
                  mb: 2,
                  boxShadow: theme.shadows[3]
                }}
              >
                <PersonIcon sx={{ fontSize: 60 }} />
              </Avatar>
              
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 0.5 }}>
                {user?.full_name || 'User'}
              </Typography>
              
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {user?.email || 'user@example.com'}
              </Typography>
              
              <AIPoweredBadge
                icon={<PhoneIcon />}
                label="Voice Agent Enabled"
                sx={{ mb: 3 }}
              />
              
              <Divider sx={{ width: '100%', my: 2 }} />
              
              <Box sx={{ width: '100%' }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Account Type
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  Administrator
                </Typography>
                
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Member Since
                </Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* Settings Tabs */}
        <Grid item xs={12} md={8}>
          <Card 
            sx={{ 
              borderRadius: 2,
              bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
              boxShadow: theme.shadows[2]
            }}
          >
            <CardContent sx={{ p: 0 }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs 
                  value={tabValue} 
                  onChange={handleTabChange}
                  sx={{ 
                    '& .MuiTab-root': { 
                      py: 2,
                      px: 3,
                      fontWeight: 500,
                    }
                  }}
                >
                  <Tab 
                    icon={<PhoneIcon />} 
                    iconPosition="start" 
                    label="Voice Agent" 
                    id="profile-tab-0"
                    aria-controls="profile-tabpanel-0"
                  />
                  <Tab 
                    icon={<SettingsIcon />} 
                    iconPosition="start" 
                    label="Account Settings" 
                    id="profile-tab-1"
                    aria-controls="profile-tabpanel-1"
                  />
                </Tabs>
              </Box>
              
              <TabPanel value={tabValue} index={0}>
                <GlobalVoiceSettings />
              </TabPanel>
              
              <TabPanel value={tabValue} index={1}>
                <Typography variant="h6" gutterBottom>
                  Account Settings
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Account settings will be available in a future update.
                </Typography>
              </TabPanel>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 