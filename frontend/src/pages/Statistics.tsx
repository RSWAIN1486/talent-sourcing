import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  People as PeopleIcon,
  Work as WorkIcon,
  Phone as PhoneIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { jobsApi } from '../services/api';

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={2}>
          <Box
            sx={{
              backgroundColor: `${color}20`,
              borderRadius: '50%',
              p: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          <Box>
            <Typography variant="h4" fontWeight="bold">
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Statistics() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['jobStats'],
    queryFn: jobsApi.getJobStats,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (!stats) {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h6" color="error">Failed to load statistics</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h1" mb={4}>Statistics</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Jobs"
            value={stats.total_jobs}
            icon={<WorkIcon sx={{ color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Candidates"
            value={stats.total_candidates}
            icon={<PeopleIcon sx={{ color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Resume Screened"
            value={stats.resume_screened}
            icon={<AssignmentIcon />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Phone Screened"
            value={stats.phone_screened}
            icon={<PhoneIcon />}
            color="#f44336"
          />
        </Grid>
      </Grid>

      {/* Additional statistics or charts can be added here */}
    </Box>
  );
} 