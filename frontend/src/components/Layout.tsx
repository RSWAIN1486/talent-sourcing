import { Box, AppBar, Toolbar, IconButton, Typography, Button, useTheme, Tooltip, Chip } from '@mui/material';
import { Outlet, useNavigate } from 'react-router-dom';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import WorkIcon from '@mui/icons-material/Work';
import BarChartIcon from '@mui/icons-material/BarChart';
import LogoutIcon from '@mui/icons-material/Logout';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { useColorMode } from '../contexts/ColorModeContext';
import { styled } from '@mui/material/styles';

// Styled components for better theme toggle
const ThemeToggleButton = styled(IconButton)(({ theme }) => ({
  position: 'relative',
  borderRadius: '12px',
  padding: '8px 12px',
  transition: 'all 0.3s ease',
  backgroundColor: theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.05)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(0, 0, 0, 0.1)',
  }
}));

// Add a styled AI badge
const AIPoweredBadge = styled(Chip)(({ theme }) => ({
  borderRadius: '16px',
  height: '32px',
  padding: '0 8px',
  fontWeight: 600,
  fontSize: '0.75rem',
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(45deg, #7b1fa2 30%, #9c27b0 90%)'
    : 'linear-gradient(45deg, #9c27b0 30%, #d500f9 90%)',
  color: '#fff',
  border: 'none',
  boxShadow: theme.palette.mode === 'dark'
    ? '0 3px 5px 2px rgba(156, 39, 176, .3)'
    : '0 3px 5px 2px rgba(156, 39, 176, .2)',
  '& .MuiChip-icon': {
    color: '#fff',
  },
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.palette.mode === 'dark'
      ? '0 6px 10px 2px rgba(156, 39, 176, .4)'
      : '0 6px 10px 2px rgba(156, 39, 176, .3)',
  }
}));

const NavButton = styled(Button)(({ theme }) => ({
  borderRadius: '8px',
  padding: '6px 16px',
  marginRight: '12px',
  transition: 'all 0.2s ease',
  color: theme.palette.mode === 'dark' ? '#fff' : '#fff',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(255, 255, 255, 0.2)',
  }
}));

const ActionButton = styled(IconButton)(({ theme }) => ({
  position: 'relative',
  borderRadius: '12px',
  padding: '8px 12px',
  marginLeft: '8px',
  transition: 'all 0.3s ease',
  backgroundColor: theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.05)',
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(0, 0, 0, 0.1)',
  }
}));

export default function Layout() {
  const { toggleColorMode, mode } = useColorMode();
  const theme = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar 
        position="fixed"
        sx={{
          bgcolor: theme.palette.mode === 'dark' 
            ? 'rgba(0, 0, 0, 0.9)' 
            : 'primary.main',
          backdropFilter: 'blur(8px)',
          borderBottom: `1px solid ${
            theme.palette.mode === 'dark'
              ? 'rgba(255, 255, 255, 0.1)'
              : 'rgba(0, 0, 0, 0.1)'
          }`,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box display="flex" alignItems="center">
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                mr: 2,
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                  : 'linear-gradient(45deg, #fff 30%, #e3f2fd 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 600,
                cursor: 'pointer',
              }}
              onClick={() => navigate('/')}
            >
              AI Recruiter
            </Typography>
            
            {/* Add AI Powered badge */}
            <AIPoweredBadge
              icon={<SmartToyIcon />}
              label="AI Powered"
              sx={{ mr: 3 }}
            />
            
            <Box>
              <NavButton
                startIcon={<WorkIcon />}
                onClick={() => navigate('/jobs')}
              >
                Jobs
              </NavButton>
              <NavButton
                startIcon={<BarChartIcon />}
                onClick={() => navigate('/stats')}
              >
                Statistics
              </NavButton>
            </Box>
          </Box>
          <Box display="flex" alignItems="center">
            <ThemeToggleButton 
              onClick={toggleColorMode}
              color="inherit"
              size="large"
              aria-label="toggle dark mode"
            >
              {mode === 'dark' ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Brightness7Icon />
                  <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                    Light
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Brightness4Icon />
                  <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
                    Dark
                  </Typography>
                </Box>
              )}
            </ThemeToggleButton>
            <Tooltip title="Logout">
              <ActionButton
                onClick={handleLogout}
                color="inherit"
                aria-label="logout"
              >
                <LogoutIcon />
              </ActionButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          bgcolor: 'background.default',
          mt: 8
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
} 