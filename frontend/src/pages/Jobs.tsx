import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  TextField,
  Typography,
  CircularProgress,
  Checkbox,
  AppBar,
  Toolbar,
  IconButton,
  Fade,
  Theme,
  useTheme,
  Paper,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Close as CloseIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { jobsApi, Job } from '../services/api';
import { ChangeEvent } from 'react';
import WorkIcon from '@mui/icons-material/Work';
import GroupIcon from '@mui/icons-material/Group';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SearchIcon from '@mui/icons-material/Search';

interface JobFormData {
  title: string;
  description: string;
  responsibilities: string;
  requirements: string;
}

const defaultValues: JobFormData = {
  title: 'Senior Full Stack Engineer',
  description: 'We are seeking a highly skilled Senior Full Stack Engineer to lead the development of scalable, high-performance web applications. You will work across the entire tech stack, from front-end interfaces to back-end services, ensuring seamless integration and top-notch user experience. This role requires strong problem-solving skills, a deep understanding of modern web technologies, and the ability to mentor junior developers.',
  responsibilities: `- Design, develop, and maintain scalable front-end and back-end systems.
- Architect and optimize databases, APIs, and cloud-based services.
- Write clean, maintainable, and efficient code using modern frameworks and languages (React, Node.js, Python, etc.).
- Ensure security, performance, and reliability of applications.
- Collaborate with product managers, designers, and other engineers to deliver high-quality solutions.
- Conduct code reviews and mentor junior developers.
- Implement DevOps best practices, CI/CD pipelines, and cloud deployments.
- Troubleshoot, debug, and enhance existing systems to improve performance.`,
  requirements: `- 5+ years of full-stack development experience.
- Proficiency in front-end frameworks (React, Angular, or Vue.js) and back-end technologies (Node.js, Python, Java, or Ruby).
- Strong database experience (SQL, NoSQL).
- Experience with cloud platforms (AWS, Azure, or GCP).
- Knowledge of RESTful APIs, GraphQL, and microservices architecture.
- Familiarity with Agile methodologies and DevOps practices.
- Excellent problem-solving and communication skills.`,
};

export default function Jobs() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [error, setError] = useState<string>('');
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const theme = useTheme();

  const { register, handleSubmit, reset, formState: { errors } } = useForm<JobFormData>({
    defaultValues,
  });

  // Fetch jobs
  const { data: jobs, isLoading, error: fetchError } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      try {
        return await jobsApi.getJobs();
      } catch (error: any) {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token');
          navigate('/login');
        }
        throw error;
      }
    },
    retry: 1,
    staleTime: 30000,
  });

  // Delete multiple jobs mutation
  const deleteJobsMutation = useMutation({
    mutationFn: async (jobIds: string[]) => {
      await Promise.all(jobIds.map(id => jobsApi.deleteJob(id)));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setSelectedJobs(new Set());
    },
    onError: (error: Error) => {
      setError(`Failed to delete jobs: ${error.message}`);
    },
  });

  // Create job mutation
  const createJobMutation = useMutation({
    mutationFn: jobsApi.createJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsDialogOpen(false);
      reset(defaultValues);
      setError('');
    },
    onError: (error: Error) => {
      setError(error.message);
    },
  });

  // Add syncAllJobsMutation
  const syncAllJobsMutation = useMutation({
    mutationFn: async () => {
      if (!jobs) return;
      const results = await Promise.allSettled(
        jobs.map(job => jobsApi.syncJobCandidates(job.id))
      );
      const errors = results
        .filter((result): result is PromiseRejectedResult => result.status === 'rejected')
        .map(result => result.reason);
      if (errors.length > 0) {
        throw new Error(`Failed to sync ${errors.length} jobs`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setError('');
    },
    onError: (error: Error) => {
      console.error('Failed to sync jobs:', error);
      setError('Failed to sync some jobs. Please try again.');
    }
  });

  const handleCreateJob = async (data: JobFormData) => {
    try {
      // Ensure all required fields are filled
      if (!data.title.trim() || !data.description.trim() || 
          !data.responsibilities.trim() || !data.requirements.trim()) {
        setError('All fields are required');
        return;
      }
      
      // Get current user ID from token
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      // Create the job with all required fields
      const newJob = await createJobMutation.mutateAsync({
        title: data.title,
        description: data.description,
        responsibilities: data.responsibilities,
        requirements: data.requirements
      });

      // Close dialog and reset form
      setIsDialogOpen(false);
      reset(defaultValues);
      setError('');
      
      // Validate and navigate to the new job's page
      if (newJob && newJob.id && /^[0-9a-fA-F]{24}$/.test(newJob.id)) {
        // Wait for the jobs list to refresh
        await queryClient.invalidateQueries({ queryKey: ['jobs'] });
        navigate(`/jobs/${newJob.id}`);
      } else {
        console.error('Invalid job ID received:', newJob);
        setError('Job created but received invalid ID');
      }
    } catch (err) {
      console.error('Failed to create job:', err);
      setError(err instanceof Error ? err.message : 'Failed to create job');
    }
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    reset(defaultValues);
    setError('');
  };

  const handleSelectJob = (jobId: string, checked: boolean) => {
    const newSelected = new Set(selectedJobs);
    if (checked) {
      newSelected.add(jobId);
    } else {
      newSelected.delete(jobId);
    }
    setSelectedJobs(newSelected);
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked && jobs) {
      setSelectedJobs(new Set(jobs.map(job => job.id)));
    } else {
      setSelectedJobs(new Set());
    }
  };

  const handleDeleteSelected = () => {
    if (selectedJobs.size === 0) return;
    
    const message = selectedJobs.size === 1 
      ? 'Are you sure you want to delete this job?' 
      : `Are you sure you want to delete these ${selectedJobs.size} jobs?`;
    
    if (window.confirm(message)) {
      deleteJobsMutation.mutate(Array.from(selectedJobs));
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (fetchError) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <Typography color="error">Error loading jobs. Please try again.</Typography>
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
      {/* Selection Toolbar - Enhanced styling */}
      <Fade in={selectedJobs.size > 0}>
        <AppBar 
          position="fixed" 
          color="default" 
          elevation={2}
          sx={{ 
            top: 64,
            backdropFilter: 'blur(8px)',
            backgroundColor: theme.palette.mode === 'dark' 
              ? 'rgba(0, 0, 0, 0.8)' 
              : 'rgba(255, 255, 255, 0.8)',
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => setSelectedJobs(new Set())}
              aria-label="clear selection"
            >
              <CloseIcon />
            </IconButton>
            <Typography sx={{ ml: 2, flex: 1 }}>
              {selectedJobs.size} {selectedJobs.size === 1 ? 'job' : 'jobs'} selected
            </Typography>
            <Button
              startIcon={<DeleteIcon />}
              color="error"
              onClick={handleDeleteSelected}
              disabled={deleteJobsMutation.isPending}
            >
              Delete
            </Button>
          </Toolbar>
        </AppBar>
      </Fade>

      {/* Enhanced Header Section */}
      <Paper 
        elevation={0}
        sx={{ 
          p: { xs: 2, sm: 3 },
          mb: 4,
          bgcolor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'rgba(0, 0, 0, 0.02)',
          borderRadius: 2,
        }}
      >
        <Box display="flex" flexDirection={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'stretch', sm: 'center' }} gap={2}>
          <Box display="flex" alignItems="center">
            <WorkIcon 
              sx={{ 
                fontSize: 40, 
                mr: 2,
                color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main'
              }} 
            />
            <Box>
              <Box display="flex" alignItems="center">
                <Typography 
                  variant="h4"
                  sx={{
                    fontWeight: 600,
                    background: theme.palette.mode === 'dark'
                      ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                      : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  Jobs
                </Typography>
                {jobs && jobs.length > 0 && (
                  <Checkbox
                    checked={selectedJobs.size === jobs.length}
                    indeterminate={selectedJobs.size > 0 && selectedJobs.size < jobs.length}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    sx={{ ml: 2 }}
                  />
                )}
              </Box>
              {jobs && (
                <Typography variant="subtitle1" color="text.secondary">
                  {jobs.length} {jobs.length === 1 ? 'position' : 'positions'} available
                </Typography>
              )}
            </Box>
          </Box>

          <Box display="flex" gap={2} flexWrap="wrap">
            <Button
              variant="outlined"
              startIcon={<CloudUploadIcon />}
              onClick={() => syncAllJobsMutation.mutate()}
              disabled={syncAllJobsMutation.isPending || !jobs?.length}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none',
                px: 3,
                flex: { xs: 1, sm: 'initial' }
              }}
            >
              {syncAllJobsMutation.isPending ? 'Syncing...' : 'Sync All Jobs'}
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setIsDialogOpen(true)}
              sx={{
                borderRadius: 2,
                textTransform: 'none',
                px: 3,
                flex: { xs: 1, sm: 'initial' },
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                  : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
                boxShadow: '0 3px 5px 2px rgba(33, 150, 243, .3)',
                '&:hover': {
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(45deg, #64b5f6 30%, #42a5f5 90%)'
                    : 'linear-gradient(45deg, #1565c0 30%, #1976d2 90%)',
                }
              }}
            >
              Create Job
            </Button>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Typography 
          color="error" 
          sx={{ mt: 2, mb: 2 }}
          component="div"
        >
          {error}
        </Typography>
      )}

      <Grid container spacing={3}>
        {jobs?.map((job: Job) => (
          <Grid item xs={12} md={6} lg={4} key={job.id}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 2,
                transition: 'all 0.3s ease',
                bgcolor: theme.palette.mode === 'dark' 
                  ? 'rgba(255, 255, 255, 0.05)' 
                  : 'background.paper',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.palette.mode === 'dark'
                    ? '0 8px 24px rgba(0,0,0,0.5)'
                    : '0 8px 24px rgba(0,0,0,0.1)',
                }
              }}
            >
              <CardContent sx={{ p: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Box display="flex" alignItems="flex-start" mb={2}>
                  <Checkbox
                    checked={selectedJobs.has(job.id)}
                    onChange={(e) => handleSelectJob(job.id, e.target.checked)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Box flex={1} onClick={() => navigate(`/jobs/${job.id}`)} sx={{ cursor: 'pointer' }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <AssignmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {job.title}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {job.description}
                    </Typography>
                  </Box>
                </Box>

                <Box mt="auto" pt={2} borderTop={1} borderColor="divider">
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Box display="flex" alignItems="center">
                        <GroupIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography variant="subtitle2" fontWeight={600}>
                          {job.total_candidates || 0} Candidates
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center">
                        <SearchIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                          {job.resume_screened || 0} Screened
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box display="flex" alignItems="center">
                        <PhoneInTalkIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                          {job.phone_screened || 0} Interviewed
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create Job Dialog */}
      <Dialog 
        open={isDialogOpen} 
        onClose={handleCloseDialog} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 2,
            bgcolor: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
            backgroundImage: 'none', // This removes transparency
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 8px 32px 0 rgba(0, 0, 0, 0.5)' 
              : '0 8px 32px 0 rgba(31, 38, 135, 0.2)',
          }
        }}
      >
        <DialogTitle
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            pb: 2
          }}
        >
          <Typography variant="h5" component="div" fontWeight={600}>
            Create New Job
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ mt: 2 }}>
          {error && (
            <Typography 
              color="error" 
              sx={{ mt: 2, mb: 1 }}
              component="div"
            >
              {error}
            </Typography>
          )}
          <Box display="flex" flexDirection="column" gap={3} mt={1}>
            <TextField
              label="Title"
              fullWidth
              {...register('title', { 
                required: 'Title is required',
                minLength: { value: 3, message: 'Title must be at least 3 characters' }
              })}
              error={!!errors.title}
              helperText={errors.title?.message}
              InputProps={{
                sx: {
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : '#fff',
                }
              }}
            />
            <TextField
              label="Description"
              fullWidth
              multiline
              rows={4}
              {...register('description', { 
                required: 'Description is required',
                minLength: { value: 10, message: 'Description must be at least 10 characters' }
              })}
              error={!!errors.description}
              helperText={errors.description?.message}
              InputProps={{
                sx: {
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : '#fff',
                }
              }}
            />
            <TextField
              label="Responsibilities"
              fullWidth
              multiline
              rows={4}
              {...register('responsibilities', { 
                required: 'Responsibilities are required',
                minLength: { value: 10, message: 'Responsibilities must be at least 10 characters' }
              })}
              error={!!errors.responsibilities}
              helperText={errors.responsibilities?.message}
              InputProps={{
                sx: {
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : '#fff',
                }
              }}
            />
            <TextField
              label="Requirements"
              fullWidth
              multiline
              rows={4}
              {...register('requirements', { 
                required: 'Requirements are required',
                minLength: { value: 10, message: 'Requirements must be at least 10 characters' }
              })}
              error={!!errors.requirements}
              helperText={errors.requirements?.message}
              InputProps={{
                sx: {
                  bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : '#fff',
                }
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: 1, borderColor: 'divider' }}>
          <Button 
            onClick={handleCloseDialog}
            sx={{ 
              borderRadius: 2,
              px: 3,
              color: theme.palette.mode === 'dark' ? 'grey.300' : 'grey.700'
            }}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={createJobMutation.isPending}
            sx={{
              borderRadius: 2,
              px: 3,
              background: theme.palette.mode === 'dark'
                ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
            }}
          >
            {createJobMutation.isPending ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              'Create'
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 