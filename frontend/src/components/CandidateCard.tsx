import React from 'react';
import { Card, CardContent, Typography, Button, Box, Chip, Grid } from '@mui/material';
import { jobsApi, Candidate } from '../services/api';

interface CandidateCardProps {
  candidate: Candidate;
}

const CandidateCard: React.FC<CandidateCardProps> = ({ candidate }) => {
  const handleDownload = async () => {
    try {
      await jobsApi.downloadResume(candidate.job_id, candidate.id);
    } catch (error) {
      console.error('Error downloading resume:', error);
    }
  };

  const handleScreening = async () => {
    try {
      await jobsApi.screenCandidate(candidate.job_id, candidate.id);
    } catch (error) {
      console.error('Error initiating screening:', error);
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" component="div">
              {candidate.name}
            </Typography>
            <Typography color="textSecondary" gutterBottom>
              {candidate.email}
            </Typography>
            {candidate.phone && (
              <Typography color="textSecondary">
                Phone: {candidate.phone}
              </Typography>
            )}
            {candidate.location && (
              <Typography color="textSecondary">
                Location: {candidate.location}
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} md={4}>
            <Box display="flex" flexDirection="column" gap={1}>
              <Typography variant="subtitle1">
                Resume Score: {candidate.resume_score}%
              </Typography>
              {candidate.screening_score && (
                <Typography variant="subtitle1">
                  Screening Score: {candidate.screening_score}%
                </Typography>
              )}
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
              {Object.entries(candidate.skills).map(([skill, score]) => (
                <Chip
                  key={skill}
                  label={`${skill}: ${score}%`}
                  color={score >= 70 ? 'primary' : 'default'}
                  variant={score >= 70 ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleDownload}
              >
                Download Resume
              </Button>
              <Button
                variant="outlined"
                color="secondary"
                onClick={handleScreening}
                disabled={!!candidate.screening_score}
              >
                {candidate.screening_score ? 'Screened' : 'Start Screening'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CandidateCard; 