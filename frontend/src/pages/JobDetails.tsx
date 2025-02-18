import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Paper,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
} from '@mui/material';
import BusinessIcon from '@mui/icons-material/Business';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PhoneIcon from '@mui/icons-material/Phone';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Job, Candidate, jobsApi } from '../services/api';
import { styled } from '@mui/material/styles';

interface CandidateFormData {
  name: string;
  email: string;
  phone?: string;
  location?: string;
  resume: FileList;
}

interface JobDisplayData {
  title: string;
  company: string;
  location: string;
  type: string;
  salary: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
}

const VisuallyHiddenInput = styled('input', {
  shouldForwardProp: (prop) => prop !== 'type'
})({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

export default function JobDetails() {
  const theme = useTheme();
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm<CandidateFormData>();

  const { data: job, isLoading: isJobLoading } = useQuery({
    queryKey: ['job', id],
    queryFn: async () => {
      if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
        throw new Error('Invalid job ID');
      }
      return jobsApi.getJob(id);
    },
    enabled: !!id && /^[0-9a-fA-F]{24}$/.test(id)
  });

  const { data: candidates, isLoading: isCandidatesLoading } = useQuery({
    queryKey: ['candidates', id],
    queryFn: async () => {
      if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
        throw new Error('Invalid job ID');
      }
      return jobsApi.getCandidates(id);
    },
    enabled: !!id && /^[0-9a-fA-F]{24}$/.test(id)
  });

  const createCandidateMutation = useMutation({
    mutationFn: (data: CandidateFormData) => {
      if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
        throw new Error('Invalid job ID');
      }
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('email', data.email);
      if (data.phone) formData.append('phone', data.phone);
      if (data.location) formData.append('location', data.location);
      formData.append('resume', data.resume[0]);
      return jobsApi.createCandidate(id, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
      setIsDialogOpen(false);
      reset();
    },
  });

  const deleteCandidateMutation = useMutation({
    mutationFn: (candidateId: string) => {
      if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
        throw new Error('Invalid job ID');
      }
      return jobsApi.deleteCandidate(id, candidateId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const syncCandidatesMutation = useMutation({
    mutationFn: () => {
      if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
        throw new Error('Invalid job ID');
      }
      return jobsApi.syncJobCandidates(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const handleCreateCandidate = (data: CandidateFormData) => {
    createCandidateMutation.mutate(data);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    reset();
  };

  const [jobDisplay] = useState<JobDisplayData>({
    title: "Senior Software Engineer",
    company: "Tech Corp",
    location: "San Francisco, CA",
    type: "Full-time",
    salary: "$120,000 - $180,000",
    description: "We are looking for a Senior Software Engineer to join our team...",
    requirements: [
      "Bachelor's degree in Computer Science or related field",
      "5+ years of experience in software development",
      "Strong proficiency in React and TypeScript",
      "Experience with cloud platforms (AWS/Azure/GCP)",
    ],
    responsibilities: [
      "Lead development of new features and products",
      "Mentor junior developers",
      "Participate in architectural decisions",
      "Write clean, maintainable code",
    ],
  });

  const handleDeleteCandidate = (candidateId: string) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      deleteCandidateMutation.mutate(candidateId);
    }
  };

  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.length) return;
    
    setIsUploading(true);
    setUploadError(null);
    setUploadProgress('Preparing files...');
    
    try {
      const files = Array.from(event.target.files);
      const validFiles = files.filter(file => 
        file.type === 'application/pdf' || 
        file.name.toLowerCase().endsWith('.pdf') ||
        file.type === 'application/zip' ||
        file.name.toLowerCase().endsWith('.zip')
      );

      if (validFiles.length === 0) {
        setUploadError('Please upload PDF files or a ZIP file containing PDFs');
        return;
      }

      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        setUploadProgress(`Uploading ${file.name} (${i + 1}/${validFiles.length})...`);
        
        const formData = new FormData();
        formData.append('file', file);
        
        if (!id) throw new Error('Job ID is missing');
        
        // Upload file
        await jobsApi.createCandidate(id, formData);
        
        setUploadProgress(`Analyzing ${file.name} with AI...`);
        // The analysis happens on the backend, we just show the message
        await new Promise(resolve => setTimeout(resolve, 1000)); // Give time to show the message
      }

      setUploadProgress('All files processed successfully!');
      
      // Refresh candidates list
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      
      // Clear the file input
      event.target.value = '';
      
      // Clear progress message after a delay
      setTimeout(() => {
        setUploadProgress('');
      }, 3000);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError(error instanceof Error ? error.message : 'Failed to upload files');
      setUploadProgress('');
    } finally {
      setIsUploading(false);
    }
  }, [id, queryClient]);

  const handleSyncCandidates = () => {
    syncCandidatesMutation.mutate();
  };

  const handleDownloadResume = async (jobId: string, candidateId: string, candidateName: string) => {
    try {
      console.log(`Attempting to download resume for ${candidateName}`);
      await jobsApi.downloadResume(jobId, candidateId);
    } catch (error) {
      console.error('Error downloading resume:', error);
      // You might want to show an error message to the user here
    }
  };

  const handleScreenCandidate = async (jobId: string, candidateId: string) => {
    try {
      if (!window.confirm('Are you sure you want to initiate a screening call with this candidate?')) {
        return;
      }
      
      await jobsApi.screenCandidate(jobId, candidateId);
      
      // Refresh the candidates list to get the updated screening score
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      
      // Show success message (you might want to add a proper notification system)
      alert('Screening call initiated successfully!');
    } catch (error) {
      console.error('Error initiating screening call:', error);
      alert('Failed to initiate screening call. Please try again.');
    }
  };

  if (isJobLoading || isCandidatesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (!job) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography color="error">Job not found</Typography>
      </Box>
    );
  }

  const formattedDate = new Date(job.created_at).toLocaleDateString();

  return (
    <Box sx={{ maxWidth: '100%', px: 3 }}>
      <Paper
        elevation={0}
        sx={{
          p: 3,
          mb: 3,
          backgroundColor: theme.palette.mode === 'dark' 
            ? theme.palette.grey[900] 
            : theme.palette.grey[100],
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {job.title}
            </Typography>
            <Typography color="text.secondary">
              Created: {formattedDate}
            </Typography>
          </Box>
          <Button
            variant="contained"
            onClick={handleSyncCandidates}
            disabled={syncCandidatesMutation.isPending}
            startIcon={<CloudUploadIcon />}
          >
            {syncCandidatesMutation.isPending ? 'Syncing...' : 'Sync Candidate Count'}
          </Button>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Job Description
              </Typography>
              <Typography paragraph>{job.description}</Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ mt: 3 }}>
                    Key Responsibilities
                  </Typography>
                  <Box component="ul" sx={{ mt: 1, mb: 2, pl: 2 }}>
                    {job.responsibilities.split('\n').map((responsibility, index) => (
                      responsibility.trim() && (
                        <Typography
                          key={index}
                          component="li"
                          sx={{ 
                            display: 'list-item',
                            mb: 1,
                            '&::marker': {
                              color: theme.palette.text.secondary
                            }
                          }}
                        >
                          {responsibility.replace(/^-\s*/, '')}
                        </Typography>
                      )
                    ))}
                  </Box>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="h6" component="h2" gutterBottom sx={{ mt: 3 }}>
                    Requirements
                  </Typography>
                  <Box component="ul" sx={{ mt: 1, mb: 2, pl: 2 }}>
                    {job.requirements.split('\n').map((requirement, index) => (
                      requirement.trim() && (
                        <Typography
                          key={index}
                          component="li"
                          sx={{ 
                            display: 'list-item',
                            mb: 1,
                            '&::marker': {
                              color: theme.palette.text.secondary
                            }
                          }}
                        >
                          {requirement.replace(/^-\s*/, '')}
                        </Typography>
                      )
                    ))}
                  </Box>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, mb: 2 }}>
                <Box
                  component="input"
                  type="file"
                  id="resume-upload"
                  multiple
                  accept=".pdf,.zip"
                  onChange={handleFileUpload}
                  sx={{
                    display: 'none'
                  }}
                />
                <Box display="flex" alignItems="center" gap={2}>
                  <Button
                    component="label"
                    htmlFor="resume-upload"
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                    disabled={isUploading}
                  >
                    {isUploading ? 'Processing...' : 'Upload Resumes'}
                  </Button>
                  {uploadProgress && (
                    <Typography color="primary">
                      {uploadProgress}
                    </Typography>
                  )}
                </Box>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                  Upload multiple PDF files or a ZIP file containing PDFs
                </Typography>
                {uploadError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {uploadError}
                  </Alert>
                )}
              </Box>

              <TableContainer>
                <Table size="medium">
                  <TableHead>
                    <TableRow>
                      <TableCell width="15%">Name</TableCell>
                      <TableCell width="15%">Email</TableCell>
                      <TableCell width="12%">Phone</TableCell>
                      <TableCell width="8%">Location</TableCell>
                      <TableCell width="10%">Resume Score</TableCell>
                      <TableCell width="10%">Screen Score</TableCell>
                      <TableCell width="20%">Top Skills</TableCell>
                      <TableCell width="10%">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {candidates?.map((candidate) => (
                      <TableRow key={candidate.id}>
                        <TableCell>{candidate.name}</TableCell>
                        <TableCell>{candidate.email}</TableCell>
                        <TableCell>{candidate.phone || 'N/A'}</TableCell>
                        <TableCell>{candidate.location || '-'}</TableCell>
                        <TableCell>
                          {candidate.resume_score.toFixed(1)}
                        </TableCell>
                        <TableCell>
                          {candidate.screening_score != null 
                            ? candidate.screening_score.toFixed(1) 
                            : 'Not Screened'}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1} flexWrap="wrap">
                            {Object.entries(candidate.skills)
                              .sort(([, a], [, b]) => b - a)
                              .slice(0, 3)
                              .map(([skill, score]) => (
                                <Chip
                                  key={skill}
                                  label={`${skill} (${(score * 100).toFixed(0)}%)`}
                                  size="small"
                                />
                              ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <IconButton
                              size="small"
                              onClick={() => handleDownloadResume(candidate.job_id, candidate.id, candidate.name)}
                              aria-label={`Download ${candidate.name}'s resume`}
                            >
                              <DownloadIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleScreenCandidate(candidate.job_id, candidate.id)}
                              disabled={!candidate.phone || candidate.screening_score != null}
                              aria-label={`Screen ${candidate.name}`}
                              color="primary"
                            >
                              <PhoneIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteCandidate(candidate.id)}
                              aria-label={`Delete ${candidate.name}'s application`}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Skills Required
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {['React', 'TypeScript', 'Node.js', 'AWS', 'Git'].map((skill) => (
                  <Chip
                    key={skill}
                    label={skill}
                    color="primary"
                    variant="outlined"
                    sx={{ m: 0.5 }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
} 