import {
  AppBar,
  Box,
  Button,
  IconButton,
  Tab,
  Tabs,
  Toolbar,
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useLocation, useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';

interface NavbarProps {
  onToggleTheme: () => void;
  mode: 'light' | 'dark';
}

export default function Navbar({ onToggleTheme, mode }: NavbarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    authApi.logout();
    navigate('/login');
  };

  const getActiveTab = () => {
    const path = location.pathname;
    if (path === '/') return 0;
    if (path.startsWith('/jobs')) return 1;
    if (path.startsWith('/stats')) return 2;
    return 0;
  };

  return (
    <AppBar 
      position="fixed"
      sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        height: 64 
      }}
    >
      <Toolbar sx={{ minHeight: 64 }}>
        <Box sx={{ flexGrow: 1 }}>
          <Tabs value={getActiveTab()} textColor="inherit">
            <Tab label="Dashboard" onClick={() => navigate('/')} />
            <Tab label="Jobs" onClick={() => navigate('/jobs')} />
            <Tab label="Statistics" onClick={() => navigate('/stats')} />
          </Tabs>
        </Box>
        <IconButton onClick={onToggleTheme} color="inherit" sx={{ mr: 1 }}>
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
        <Button color="inherit" onClick={handleLogout}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
} 