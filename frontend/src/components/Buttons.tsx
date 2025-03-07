import { Button, styled } from '@mui/material';

export const GradientButton = styled(Button)(({ theme }) => ({
  borderRadius: '8px',
  padding: '12px 24px',
  fontWeight: 600,
  textTransform: 'none',
  fontSize: '1rem',
  boxShadow: theme.palette.mode === 'dark' 
    ? '0 4px 14px 0 rgba(0, 0, 0, 0.3)' 
    : '0 4px 14px 0 rgba(0, 0, 0, 0.1)',
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
    : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
  color: theme.palette.mode === 'dark' ? '#0a1929' : '#ffffff',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.palette.mode === 'dark' 
      ? '0 6px 20px 0 rgba(0, 0, 0, 0.4)' 
      : '0 6px 20px 0 rgba(0, 0, 0, 0.15)',
  }
}));

export const OutlinedButton = styled(Button)(() => ({
  borderRadius: '8px',
  textTransform: 'none',
  fontWeight: 600,
  padding: '10px 24px',
  transition: 'all 0.3s ease',
})); 