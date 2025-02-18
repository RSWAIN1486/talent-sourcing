import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  IconButton,
  Tab,
  Tabs,
  Toolbar,
  Typography,
  useTheme,
  Button,
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import WorkIcon from '@mui/icons-material/Work';
import LogoutIcon from '@mui/icons-material/Logout';
import { authApi } from '../services/api';

interface NavbarProps {
  onToggleTheme: () => void;
  mode: 'light' | 'dark';
}

export default function Navbar({ onToggleTheme, mode }: NavbarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const getActiveTab = () => {
    const path = location.pathname;
    if (path.startsWith('/jobs')) return 0;
    if (path.startsWith('/stats')) return 1;
    return 0;
  };

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  return (
    <AppBar position="sticky" elevation={1}>
      <Toolbar>
        <WorkIcon sx={{ mr: 2 }} />
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            textDecoration: 'none',
            color: 'inherit',
            flexGrow: 1,
            display: 'flex',
            alignItems: 'center',
          }}
        >
          Talent Sourcing
        </Typography>
        <Box sx={{ flexGrow: 1 }}>
          <Tabs value={getActiveTab()} textColor="inherit" indicatorColor="secondary">
            <Tab
              label="Jobs"
              component={RouterLink}
              to="/jobs"
              sx={{ color: 'inherit' }}
            />
            <Tab
              label="Statistics"
              component={RouterLink}
              to="/stats"
              sx={{ color: 'inherit' }}
            />
          </Tabs>
        </Box>
        <IconButton onClick={onToggleTheme} color="inherit" sx={{ mr: 1 }}>
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
        <Button
          color="inherit"
          onClick={handleLogout}
          startIcon={<LogoutIcon />}
        >
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
} 