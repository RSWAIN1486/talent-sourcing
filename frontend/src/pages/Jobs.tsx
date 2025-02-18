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
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Close as CloseIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { jobsApi, Job } from '../services/api';
import { ChangeEvent } from 'react';

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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (fetchError) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography color="error">Error loading jobs. Please try again.</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Selection Toolbar */}
      <Fade in={selectedJobs.size > 0}>
        <AppBar 
          position="fixed" 
          color="default" 
          sx={{ 
            top: 0,
            left: 0,
            right: 0,
            zIndex: (theme: Theme) => theme.zIndex.drawer + 1
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

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Box display="flex" alignItems="center">
          <Typography variant="h1">Jobs</Typography>
          {jobs && jobs.length > 0 && (
            <Checkbox
              checked={selectedJobs.size === jobs.length}
              indeterminate={selectedJobs.size > 0 && selectedJobs.size < jobs.length}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleSelectAll(e.target.checked)}
              sx={{ ml: 2 }}
              aria-label="select all jobs"
            />
          )}
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<CloudUploadIcon />}
            onClick={() => syncAllJobsMutation.mutate()}
            disabled={syncAllJobsMutation.isPending || !jobs?.length}
            sx={{ mr: 2 }}
          >
            {syncAllJobsMutation.isPending ? 'Syncing...' : 'Sync All Jobs'}
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsDialogOpen(true)}
          >
            Create Job
          </Button>
        </Box>
      </Box>

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
          <Grid item xs={12} sm={6} md={4} key={job.id}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="flex-start">
                  <Checkbox
                    checked={selectedJobs.has(job.id)}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => handleSelectJob(job.id, e.target.checked)}
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                    aria-label={`select ${job.title}`}
                  />
                  <Box 
                    flex={1} 
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/jobs/${job.id}`)}
                  >
                    <Typography variant="h6" gutterBottom>
                      {job.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {job.description.slice(0, 150)}...
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={1}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" color="text.secondary">
                          Total Candidates: {job.total_candidates || 0}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2" color="text.secondary">
                          Resume Screened: {job.resume_screened || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Phone Screened: {job.phone_screened || 0}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
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
        aria-labelledby="create-job-dialog-title"
        keepMounted={false}
        disablePortal={false}
        sx={{
          '& .MuiDialog-container': {
            alignItems: 'flex-start',
            pt: 8
          }
        }}
      >
        <Box 
          component="form" 
          onSubmit={handleSubmit(handleCreateJob)}
          noValidate
          autoComplete="off"
        >
          <DialogTitle id="create-job-dialog-title">Create New Job</DialogTitle>
          <DialogContent>
            {error && (
              <Typography 
                color="error" 
                sx={{ mt: 2, mb: 1 }}
                component="div"
              >
                {error}
              </Typography>
            )}
            <Box display="flex" flexDirection="column" gap={2} mt={1}>
              <TextField
                label="Title"
                fullWidth
                {...register('title', { 
                  required: 'Title is required',
                  minLength: { value: 3, message: 'Title must be at least 3 characters' }
                })}
                error={!!errors.title}
                helperText={errors.title?.message}
                inputProps={{
                  'aria-label': 'Job title'
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
                inputProps={{
                  'aria-label': 'Job description'
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
                inputProps={{
                  'aria-label': 'Job responsibilities'
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
                inputProps={{
                  'aria-label': 'Job requirements'
                }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createJobMutation.isPending}
            >
              {createJobMutation.isPending ? <CircularProgress size={24} /> : 'Create'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
} 