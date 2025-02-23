import { jobsApi, Candidate } from '../services/api';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';
import { DownloadOutlined } from '@mui/icons-material';

interface CandidateCardProps {
  candidate: Candidate;
}

const CandidateCard: React.FC<CandidateCardProps> = ({ candidate }) => {
  const handleDownload = () => {
    jobsApi.downloadResume(candidate.job_id, candidate.id);
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h6">{candidate.name}</Typography>
            <Typography color="text.secondary">{candidate.email}</Typography>
            {candidate.phone && (
              <Typography color="text.secondary">{candidate.phone}</Typography>
            )}
            {candidate.location && (
              <Typography color="text.secondary">{candidate.location}</Typography>
            )}
          </Box>
          <Button
            variant="outlined"
            startIcon={<DownloadOutlined />}
            onClick={handleDownload}
          >
            Download Resume
          </Button>
        </Box>
        <Box mt={2}>
          <Typography variant="subtitle1">Skills:</Typography>
          <Box display="flex" flexWrap="wrap" gap={1}>
            {Object.entries(candidate.skills).map(([skill, score]) => (
              <Typography key={skill} variant="body2" color="text.secondary">
                {skill}: {(score * 100).toFixed(0)}%
              </Typography>
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CandidateCard; 