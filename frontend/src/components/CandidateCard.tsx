import { jobsApi, Candidate } from '../services/api';

interface CandidateCardProps {
  candidate: Candidate;
}

const CandidateCard: React.FC<CandidateCardProps> = ({ candidate }) => {
  const handleDownload = () => {
    jobsApi.downloadResume(candidate.job_id, candidate.id);
  };

  return (
    // Rest of the component code
  );
};

export default CandidateCard; 