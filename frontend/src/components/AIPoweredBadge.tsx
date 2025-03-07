import { Chip, styled } from '@mui/material';

export const AIPoweredBadge = styled(Chip)(({ theme }) => ({
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