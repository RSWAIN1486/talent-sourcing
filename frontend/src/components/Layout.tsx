import { Box, AppBar, Toolbar, IconButton, Typography, Button, useTheme, Tooltip } from '@mui/material';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import WorkIcon from '@mui/icons-material/Work';
import BarChartIcon from '@mui/icons-material/BarChart';
import LogoutIcon from '@mui/icons-material/Logout';
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
    localStorage.removeItem('token');
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
                mr: 4,
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                  : 'linear-gradient(45deg, #fff 30%, #e3f2fd 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 600,
              }}
            >
              AI Recruiter
            </Typography>
            <Box>
              <NavButton
                startIcon={<WorkIcon />}
                component={Link}
                to="/jobs"
              >
                Jobs
              </NavButton>
              <NavButton
                startIcon={<BarChartIcon />}
                component={Link}
                to="/stats"
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