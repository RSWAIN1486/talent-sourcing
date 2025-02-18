import { Box, Container } from '@mui/material';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

interface LayoutProps {
  onToggleTheme: () => void;
  mode: 'light' | 'dark';
}

export default function Layout({ onToggleTheme, mode }: LayoutProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar onToggleTheme={onToggleTheme} mode={mode} />
      <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Outlet />
      </Container>
    </Box>
  );
} 