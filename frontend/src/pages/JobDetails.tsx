import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { jobsApi } from '../services/api';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import CandidateCard from '../components/CandidateCard';

export default function JobDetails() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string>('');

  // Fetch job details
  const { data: job, isLoading: isJobLoading } = useQuery({
    queryKey: ['jobs', id],
    queryFn: () => jobsApi.getJob(id!),
    enabled: !!id,
  });

  // Fetch candidates
  const { data: candidates, isLoading: isCandidatesLoading } = useQuery({
    queryKey: ['candidates', id],
    queryFn: () => jobsApi.getCandidates(id!),
    enabled: !!id,
  });

  // Upload resume mutation
  const uploadResumeMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return jobsApi.createCandidate(id!, formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      setError('');
    },
    onError: (error: Error) => {
      setError(`Failed to upload resume: ${error.message}`);
    },
  });

  // Sync candidates mutation
  const syncCandidatesMutation = useMutation({
    mutationFn: () => jobsApi.syncJobCandidates(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', id] });
      queryClient.invalidateQueries({ queryKey: ['jobs', id] });
    },
    onError: (error: Error) => {
      setError(`Failed to sync candidates: ${error.message}`);
    },
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    try {
      await uploadResumeMutation.mutateAsync(file);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const handleSyncCandidates = () => {
    syncCandidatesMutation.mutate();
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
    <Box p={3}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h4" gutterBottom>
                {job.title}
              </Typography>
              <Typography color="textSecondary" gutterBottom>
                Created on {formattedDate}
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Description
              </Typography>
              <Typography paragraph>{job.description}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Responsibilities
              </Typography>
              <Typography paragraph>{job.responsibilities}</Typography>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Requirements
              </Typography>
              <Typography paragraph>{job.requirements}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">
          Candidates ({candidates?.length || 0})
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            component="label"
            variant="contained"
            startIcon={<CloudUploadIcon />}
          >
            Upload Resume
            <input
              type="file"
              hidden
              accept=".pdf"
              onChange={handleFileUpload}
            />
          </Button>
          <Button
            variant="outlined"
            onClick={handleSyncCandidates}
            disabled={syncCandidatesMutation.isPending}
          >
            {syncCandidatesMutation.isPending ? 'Syncing...' : 'Sync Candidates'}
          </Button>
        </Box>
      </Box>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {candidates?.map((candidate) => (
        <CandidateCard key={candidate.id} candidate={candidate} />
      ))}

      {candidates?.length === 0 && (
        <Typography color="textSecondary" align="center">
          No candidates found. Upload resumes to get started.
        </Typography>
      )}
    </Box>
  );
} 