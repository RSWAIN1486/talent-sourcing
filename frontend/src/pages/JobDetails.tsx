import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Paper,
  useTheme,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Chip,
  LinearProgress,
  Tooltip
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PhoneIcon from '@mui/icons-material/Phone';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '../services/api';
import { useState } from 'react';

export default function JobDetails() {
  const theme = useTheme();
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>('');

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

  const handleDeleteCandidate = (candidateId: string) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      deleteCandidateMutation.mutate(candidateId);
    }
  };

  const handleDownloadResume = async (jobId: string, candidateId: string, candidateName: string) => {
    try {
      console.log(`Attempting to download resume for ${candidateName}`);
      await jobsApi.downloadResume(jobId, candidateId);
    } catch (error) {
      console.error('Error downloading resume:', error);
    }
  };

  const handleScreenCandidate = async (jobId: string, candidateId: string) => {
    try {
      if (!window.confirm('Are you sure you want to initiate a screening call with this candidate?')) {
        return;
      }
      
      await jobsApi.voiceScreenCandidate(jobId, candidateId);
      
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      
      alert('Voice screening call initiated successfully!');
    } catch (error) {
      console.error('Error initiating screening call:', error);
      alert('Failed to initiate screening call. Please try again.');
    }
  };

  const handleSyncCandidates = () => {
    syncCandidatesMutation.mutate();
  };

  if (isJobLoading || isCandidatesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <CircularProgress />
      </Box>
    );
  }

  if (!job) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" mt={8}>
        <Typography color="error">Job not found</Typography>
      </Box>
    );
  }

  const formattedDate = new Date(job.created_at).toLocaleDateString();

  return (
    <Box sx={{ maxWidth: '100%', px: 3, pt: 8 }}>
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
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {job.title}
            </Typography>
            <Typography color="text.secondary">
              Created: {formattedDate}
            </Typography>
          </Box>
          <Box display="flex" gap={2}>
            <Button
              variant="contained"
              component="label"
              startIcon={<CloudUploadIcon />}
              disabled={isUploading}
            >
              Upload Resume
              <input
                type="file"
                hidden
                multiple
                accept=".pdf,.zip"
                onChange={async (e) => {
                  const files = Array.from(e.target.files || []);
                  if (files.length > 0) {
                    setIsUploading(true);
                    setUploadProgress({});
                    setStatusMessage(`Preparing to process ${files.length} file${files.length > 1 ? 's' : ''}...`);
                    
                    try {
                      for (let i = 0; i < files.length; i++) {
                        const file = files[i];
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        try {
                          setStatusMessage(`Uploading ${file.name}...`);
                          await jobsApi.createCandidate(job.id, formData, (progressEvent) => {
                            if (progressEvent.total) {
                              const progress = (progressEvent.loaded / progressEvent.total) * 100;
                              setUploadProgress(prev => ({
                                ...prev,
                                [file.name]: progress
                              }));
                            }
                          });
                          
                          setStatusMessage(`Analyzing ${file.name} using AI...`);
                          // The backend is processing the file at this point
                          await new Promise(resolve => setTimeout(resolve, 1000)); // Give time for status to be visible
                          
                          setStatusMessage(`Extracting information from ${file.name}...`);
                          await new Promise(resolve => setTimeout(resolve, 1000)); // Give time for status to be visible
                          
                          setStatusMessage(`Computing skills and experience scores...`);
                          await new Promise(resolve => setTimeout(resolve, 1000)); // Give time for status to be visible
                          
                        } catch (error: any) {
                          console.error(`Error uploading ${file.name}:`, error);
                          setStatusMessage(`Failed to process ${file.name}`);
                          alert(`Failed to upload ${file.name}: ${error.response?.data?.detail || 'Unknown error'}`);
                        }
                      }
                      
                      setStatusMessage('Finalizing and updating candidate list...');
                      // Refresh data after all uploads
                      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
                      queryClient.invalidateQueries({ queryKey: ['jobs'] });
                      
                      alert('All resumes uploaded successfully!');
                    } finally {
                      setIsUploading(false);
                      setUploadProgress({});
                      setStatusMessage('');
                      e.target.value = '';
                    }
                  }
                }}
              />
            </Button>
            <Button
              variant="outlined"
              onClick={handleSyncCandidates}
              disabled={syncCandidatesMutation.isPending}
              startIcon={<CloudUploadIcon />}
            >
              {syncCandidatesMutation.isPending ? 'Syncing...' : 'Sync Candidate Count'}
            </Button>
          </Box>
        </Box>

        {isUploading && (
          <Box mb={3}>
            <Typography variant="subtitle2" gutterBottom>
              {statusMessage}
            </Typography>
            {Object.entries(uploadProgress).map(([filename, progress]) => (
              <Box key={filename} mb={1}>
                <Typography variant="body2" color="text.secondary">
                  {filename}: {Math.round(progress)}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={progress} 
                  sx={{ mt: 0.5 }}
                />
              </Box>
            ))}
          </Box>
        )}

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>Description</Typography>
          <Typography paragraph>{job.description}</Typography>

          <Typography variant="h6" gutterBottom>Responsibilities</Typography>
          <Typography paragraph style={{ whiteSpace: 'pre-line' }}>{job.responsibilities}</Typography>

          <Typography variant="h6" gutterBottom>Requirements</Typography>
          <Typography paragraph style={{ whiteSpace: 'pre-line' }}>{job.requirements}</Typography>
        </Box>

        <Box mb={4}>
          <Typography variant="h6" gutterBottom>Skills Required</Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {['React', 'TypeScript', 'Node.js', 'AWS', 'Git'].map((skill) => (
              <Chip
                key={skill}
                label={skill}
                color="primary"
                variant="outlined"
                sx={{ borderRadius: 1 }}
              />
            ))}
          </Box>
        </Box>
      </Paper>

      <Typography variant="h5" gutterBottom>Candidates</Typography>

      <TableContainer>
        <Table size="medium">
          <TableHead>
            <TableRow>
              <TableCell width="12%">Name</TableCell>
              <TableCell width="12%">Email</TableCell>
              <TableCell width="8%">Phone</TableCell>
              <TableCell width="7%">Location</TableCell>
              <TableCell width="7%">Resume Score</TableCell>
              <TableCell width="7%">Screen Score</TableCell>
              <TableCell width="7%">Notice Period</TableCell>
              <TableCell width="8%">Current Comp.</TableCell>
              <TableCell width="8%">Expected Comp.</TableCell>
              <TableCell width="14%">Top Skills</TableCell>
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
                    ? (
                      <Tooltip title={candidate.screening_summary || 'No screening summary available'}>
                        <span>{candidate.screening_score.toFixed(1)}</span>
                      </Tooltip>
                    ) 
                    : candidate.screening_in_progress
                    ? <Box display="flex" alignItems="center">
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <span>In progress</span>
                      </Box>
                    : 'Not Screened'}
                </TableCell>
                <TableCell>
                  {candidate.notice_period || '-'}
                </TableCell>
                <TableCell>
                  {candidate.current_compensation || '-'}
                </TableCell>
                <TableCell>
                  {candidate.expected_compensation || '-'}
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
                      disabled={!candidate.phone || candidate.screening_score != null || candidate.screening_in_progress}
                      aria-label={`Screen ${candidate.name}`}
                      color="primary"
                    >
                      {candidate.screening_in_progress 
                        ? <CircularProgress size={18} /> 
                        : <PhoneIcon />
                      }
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
    </Box>
  );
} 