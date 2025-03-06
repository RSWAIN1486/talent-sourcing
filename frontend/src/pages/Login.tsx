import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  useTheme,
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { authApi, LoginCredentials } from '../services/api';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useColorMode } from '../contexts/ColorModeContext';

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  const theme = useTheme();
  const { toggleColorMode, mode } = useColorMode();
  
  const { register, handleSubmit, formState: { errors } } = useForm<LoginCredentials>();

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: () => {
      navigate('/jobs');
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to login');
    },
  });

  const onSubmit = (data: LoginCredentials) => {
    setError('');
    loginMutation.mutate(data);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        transition: 'background-color 0.3s ease',
      }}
    >
      <IconButton
        onClick={toggleColorMode}
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
        }}
      >
        {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
      </IconButton>

      <Card 
        sx={{ 
          width: '100%',
          maxWidth: 400,
          bgcolor: 'background.paper',
          backdropFilter: 'blur(10px)',
          boxShadow: theme.palette.mode === 'dark' 
            ? '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
            : '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
          borderRadius: 3,
          border: `1px solid ${theme.palette.divider}`,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            boxShadow: theme.palette.mode === 'dark'
              ? '0 12px 40px 0 rgba(0, 0, 0, 0.45)'
              : '0 12px 40px 0 rgba(31, 38, 135, 0.45)',
          }
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mb: 3,
            }}
          >
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                bgcolor: 'primary.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2,
                boxShadow: theme.palette.mode === 'dark'
                  ? '0 4px 20px 0 rgba(0, 0, 0, 0.5)'
                  : '0 4px 20px 0 rgba(61, 71, 82, 0.1)',
              }}
            >
              <LockOutlinedIcon sx={{ fontSize: 32, color: 'white' }} />
            </Box>
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom
              sx={{ 
                color: 'text.primary',
                fontWeight: 700,
                letterSpacing: '-0.5px',
              }}
            >
              Welcome Back
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary"
              textAlign="center"
              sx={{ mb: 3 }}
            >
              Sign in to access your dashboard
            </Typography>
          </Box>

          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mb: 3,
                borderRadius: 2,
                bgcolor: theme.palette.mode === 'dark' 
                  ? 'rgba(211, 47, 47, 0.2)'
                  : 'rgba(211, 47, 47, 0.1)',
              }}
            >
              {error}
            </Alert>
          )}

          <Box 
            component="form" 
            onSubmit={handleSubmit(onSubmit)}
            sx={{ mt: 1 }}
          >
            <TextField
              label="Email"
              fullWidth
              {...register('username', { required: 'Email is required' })}
              error={!!errors.username}
              helperText={errors.username?.message}
              sx={{
                mb: 2.5,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  }
                }
              }}
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              {...register('password', { required: 'Password is required' })}
              error={!!errors.password}
              helperText={errors.password?.message}
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                  }
                }
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loginMutation.isPending}
              sx={{
                py: 1.8,
                borderRadius: 2,
                fontSize: '1rem',
                fontWeight: 600,
                textTransform: 'none',
                bgcolor: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.dark',
                }
              }}
            >
              {loginMutation.isPending ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
} 