import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
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
  Tooltip,
  Card,
  Divider,
  Alert,
  Collapse,
  Snackbar,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import PhoneIcon from '@mui/icons-material/Phone';
import SyncIcon from '@mui/icons-material/Sync';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '../services/api';
import { useState, ChangeEvent } from 'react';
import { styled } from '@mui/material/styles';
import MuiAlert from '@mui/material/Alert';

// Add a styled AI badge
const AIPoweredBadge = styled(Chip)(({ theme }) => ({
  borderRadius: '16px',
  height: '28px',
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

// Add this styled component for the rotate animation
const ExpandMore = styled((props: {
  expand: boolean;
  onClick: () => void;
  children?: React.ReactNode;
}) => {
  const { expand, ...other } = props;
  return <IconButton {...other}>{props.children}</IconButton>;
})(({ theme, expand }) => ({
  transform: !expand ? 'rotate(0deg)' : 'rotate(180deg)',
  marginLeft: 'auto',
  transition: theme.transitions.create('transform', {
    duration: theme.transitions.duration.shortest,
  }),
}));

export default function JobDetails() {
  const theme = useTheme();
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [expandedResp, setExpandedResp] = useState(false);
  const [expandedReq, setExpandedReq] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);

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

  const handleUploadResume = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0 && job) {
      setIsUploading(true);
      setUploadProgress({});
      
      try {
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          const formData = new FormData();
          formData.append('file', file);
          
          // Initialize progress for this file
          setUploadProgress(prev => ({
            ...prev,
            [file.name]: 0
          }));

          try {
            // Upload phase (0-30%)
            setStatusMessage(`Uploading ${file.name}...`);
            await jobsApi.createCandidate(job.id, formData, (progressEvent) => {
              if (progressEvent.total) {
                const uploadProgress = (progressEvent.loaded / progressEvent.total) * 30;
                setUploadProgress(prev => ({
                  ...prev,
                  [file.name]: uploadProgress
                }));
              }
            });
            
            // AI Analysis phase (30-60%)
            setStatusMessage(`Analyzing ${file.name} using AI...`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: 60
            }));
            
            // Information Extraction phase (60-80%)
            setStatusMessage(`Extracting information from ${file.name}...`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: 80
            }));
            
            // Final Processing phase (80-100%)
            setStatusMessage(`Computing skills and experience scores...`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: 100
            }));
            
          } catch (error: any) {
            console.error(`Error uploading ${file.name}:`, error);
            setStatusMessage(`Failed to process ${file.name}`);
            alert(`Failed to upload ${file.name}: ${error.response?.data?.detail || 'Unknown error'}`);
          }
        }
        
        queryClient.invalidateQueries({ queryKey: ['candidates', id] });
        queryClient.invalidateQueries({ queryKey: ['jobs'] });
        
        setSuccessMessage('All resumes uploaded successfully!');
        setShowSuccessAlert(true);
      } finally {
        setIsUploading(false);
        setUploadProgress({});
        setStatusMessage('');
        e.target.value = '';
      }
    }
  };

  const handleCloseSuccessAlert = () => {
    setShowSuccessAlert(false);
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
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 } }}>
      {/* Header Section with Job Details */}
      <Card 
        elevation={0}
        sx={{ 
          mb: 4,
          bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
          borderRadius: 2,
        }}
      >
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
            <Box display="flex" alignItems="center">
              <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                {job?.title}
              </Typography>
              <AIPoweredBadge
                icon={<SmartToyIcon />}
                label="AI Powered"
                sx={{ ml: 2 }}
              />
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="subtitle1" color="text.secondary">
                Created: {formattedDate}
              </Typography>
              <Button
                component="label"
                variant="contained"
                startIcon={<CloudUploadIcon />}
                disabled={isUploading}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                  background: theme.palette.mode === 'dark'
                    ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                    : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
                }}
              >
                {isUploading ? 'Uploading...' : 'Upload Resume'}
                <input
                  type="file"
                  hidden
                  multiple
                  accept=".pdf,.doc,.docx"
                  onChange={handleUploadResume}
                />
              </Button>
              <Button
                variant="outlined"
                startIcon={<SyncIcon />}
                onClick={handleSyncCandidates}
                disabled={syncCandidatesMutation.isPending}
                sx={{
                  borderRadius: 2,
                  textTransform: 'none',
                }}
              >
                {syncCandidatesMutation.isPending ? (
                  <>
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    Syncing...
                  </>
                ) : (
                  'Sync Candidates'
                )}
              </Button>
            </Box>
          </Box>

          {statusMessage && (
            <Alert 
              severity={statusMessage.includes('failed') ? 'error' : 'success'}
              sx={{ mt: 2 }}
              onClose={() => setStatusMessage('')}
            >
              {statusMessage}
            </Alert>
          )}

          <Divider sx={{ my: 3 }} />

          {/* Job Description Sections */}
          <Box>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Description
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {job?.description}
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Responsibilities
              </Typography>
              <ExpandMore
                expand={expandedResp}
                onClick={() => setExpandedResp(!expandedResp)}
                aria-expanded={expandedResp}
                aria-label="show responsibilities"
                sx={{ ml: 1 }}
              >
                <ExpandMoreIcon />
              </ExpandMore>
            </Box>
            <Collapse in={expandedResp} timeout="auto" unmountOnExit>
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ 
                  whiteSpace: 'pre-line',
                  mt: 2,
                  pl: 2,
                  borderLeft: '2px solid',
                  borderColor: 'primary.main',
                }}
              >
                {job?.responsibilities}
              </Typography>
            </Collapse>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Requirements
              </Typography>
              <ExpandMore
                expand={expandedReq}
                onClick={() => setExpandedReq(!expandedReq)}
                aria-expanded={expandedReq}
                aria-label="show requirements"
                sx={{ ml: 1 }}
              >
                <ExpandMoreIcon />
              </ExpandMore>
            </Box>
            <Collapse in={expandedReq} timeout="auto" unmountOnExit>
              <Typography 
                variant="body1" 
                color="text.secondary" 
                sx={{ 
                  whiteSpace: 'pre-line',
                  mt: 2,
                  pl: 2,
                  borderLeft: '2px solid',
                  borderColor: 'primary.main',
                }}
              >
                {job?.requirements}
              </Typography>
            </Collapse>
          </Box>
        </Box>
      </Card>

      {/* Candidates Table Section */}
      <Card 
        sx={{ 
          bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
          borderRadius: 2,
          overflow: 'hidden', // Ensures the table doesn't break the card borders
        }}
      >
        <Box sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
            Candidates ({candidates?.length || 0})
          </Typography>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Resume Score</TableCell>
                  <TableCell>Screen Score</TableCell>
                  <TableCell>Notice Period</TableCell>
                  <TableCell>Current Comp.</TableCell>
                  <TableCell>Expected Comp.</TableCell>
                  <TableCell>Top Skills</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {candidates?.map((candidate) => (
                  <TableRow 
                    key={candidate.id}
                    sx={{ 
                      '&:hover': { 
                        bgcolor: theme.palette.mode === 'dark' 
                          ? 'rgba(255, 255, 255, 0.05)' 
                          : 'rgba(0, 0, 0, 0.02)' 
                      }
                    }}
                  >
                    <TableCell sx={{ fontWeight: 500 }}>{candidate.name}</TableCell>
                    <TableCell>{candidate.email}</TableCell>
                    <TableCell>{candidate.phone || '-'}</TableCell>
                    <TableCell>{candidate.location || '-'}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: 500,
                            color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main'
                          }}
                        >
                          {candidate.resume_score}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={candidate.resume_score}
                          sx={{ 
                            width: 60,
                            height: 6,
                            borderRadius: 3,
                            bgcolor: theme.palette.mode === 'dark' 
                              ? 'rgba(255, 255, 255, 0.1)' 
                              : 'rgba(0, 0, 0, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: theme.palette.mode === 'dark' 
                                ? 'primary.light'
                                : 'primary.main',
                            }
                          }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      {candidate.screening_score ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontWeight: 500,
                              color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main'
                            }}
                          >
                            {candidate.screening_score}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={candidate.screening_score}
                            sx={{ 
                              width: 60,
                              height: 6,
                              borderRadius: 3,
                              bgcolor: theme.palette.mode === 'dark' 
                                ? 'rgba(255, 255, 255, 0.1)' 
                                : 'rgba(0, 0, 0, 0.1)',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: theme.palette.mode === 'dark' 
                                  ? 'primary.light'
                                  : 'primary.main',
                              }
                            }}
                          />
                        </Box>
                      ) : candidate.screening_in_progress ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <CircularProgress size={16} />
                          <Typography variant="body2">In progress</Typography>
                        </Box>
                      ) : (
                        'Not Screened'
                      )}
                    </TableCell>
                    <TableCell>{candidate.notice_period || '-'}</TableCell>
                    <TableCell>{candidate.current_compensation || '-'}</TableCell>
                    <TableCell>{candidate.expected_compensation || '-'}</TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {Object.entries(candidate.skills || {})
                          .sort(([, a], [, b]) => b - a)
                          .slice(0, 3)
                          .map(([skill, score]) => (
                            <Chip
                              key={skill}
                              label={`${skill} (${(score * 100).toFixed(0)}%)`}
                              size="small"
                              sx={{ 
                                bgcolor: theme.palette.mode === 'dark' 
                                  ? 'rgba(144, 202, 249, 0.2)' 
                                  : 'rgba(25, 118, 210, 0.1)',
                              }}
                            />
                          ))}
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Box display="flex" gap={1} justifyContent="flex-end">
                        <Tooltip title="Download Resume">
                          <IconButton
                            size="small"
                            onClick={() => handleDownloadResume(candidate.job_id, candidate.id, candidate.name)}
                            sx={{ 
                              color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main',
                            }}
                          >
                            <DownloadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title={
                          !candidate.phone 
                            ? 'Phone number required for screening'
                            : candidate.screening_score 
                              ? 'Already screened'
                              : 'Start screening call'
                        }>
                          <span>
                            <IconButton
                              size="small"
                              onClick={() => handleScreenCandidate(candidate.job_id, candidate.id)}
                              disabled={!candidate.phone || candidate.screening_score != null || candidate.screening_in_progress}
                              sx={{ 
                                color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.main',
                              }}
                            >
                              {candidate.screening_in_progress ? (
                                <CircularProgress size={18} />
                              ) : (
                                <PhoneIcon />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title="Delete Candidate">
                          <IconButton
                            size="small"
                            onClick={() => handleDeleteCandidate(candidate.id)}
                            sx={{ color: 'error.main' }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </Card>

      {/* Progress Overlay and Success Alert Combined */}
      <Snackbar
        open={isUploading || showSuccessAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        sx={{ top: 80 }} // Adjust based on your navbar height
      >
        <Box>
          {isUploading && (
            <Alert 
              severity="info"
              sx={{ 
                mb: 1,
                width: '100%',
                '& .MuiAlert-message': { width: '100%' }
              }}
            >
              <Typography variant="subtitle2" gutterBottom>
                {statusMessage}
              </Typography>
              {Object.entries(uploadProgress).map(([filename, progress]) => (
                <Box key={filename} sx={{ mt: 1, width: '100%', maxWidth: 400 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption">{filename}</Typography>
                    <Typography variant="caption" color="primary">
                      {Math.round(progress)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={progress}
                    sx={{ 
                      height: 4,
                      borderRadius: 2,
                      bgcolor: theme.palette.mode === 'dark' 
                        ? 'rgba(255, 255, 255, 0.1)' 
                        : 'rgba(0, 0, 0, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        transition: 'transform 0.5s ease',
                      }
                    }}
                  />
                </Box>
              ))}
            </Alert>
          )}
          {showSuccessAlert && !isUploading && (
            <MuiAlert
              elevation={6}
              variant="filled"
              onClose={handleCloseSuccessAlert}
              severity="success"
            >
              {successMessage}
            </MuiAlert>
          )}
        </Box>
      </Snackbar>
    </Box>
  );
} 