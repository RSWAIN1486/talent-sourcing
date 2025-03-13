import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Divider,
  Grid,
  IconButton,
  Tooltip,
  useTheme,
  Chip,
  Collapse,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voiceAgentApi, JobVoiceConfig, VoiceModel, VoiceInfo } from '../../services/api';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import SaveIcon from '@mui/icons-material/Save';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface JobVoiceSettingsProps {
  jobId: string;
}

export default function JobVoiceSettings({ jobId }: JobVoiceSettingsProps) {
  const theme = useTheme();
  const queryClient = useQueryClient();
  
  const [expanded, setExpanded] = useState(false);
  const [formData, setFormData] = useState<Partial<JobVoiceConfig>>({
    job_id: jobId,
    use_global_config: true,
    custom_system_prompt: '',
    custom_questions: [],
  });
  
  const [newQuestion, setNewQuestion] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Fetch job config
  const { 
    data: jobConfig, 
    isLoading: isLoadingConfig,
    error: configError 
  } = useQuery({
    queryKey: ['job-voice-config', jobId],
    queryFn: () => voiceAgentApi.getJobConfig(jobId),
    enabled: !!jobId,
  });
  
  // Fetch available models
  const { 
    data: models, 
    isLoading: isLoadingModels 
  } = useQuery({
    queryKey: ['voice-models'],
    queryFn: voiceAgentApi.getModels,
  });
  
  // Fetch available voices
  const { 
    data: voices, 
    isLoading: isLoadingVoices 
  } = useQuery({
    queryKey: ['voice-voices'],
    queryFn: voiceAgentApi.getVoices,
  });
  
  // Update job config mutation
  const updateConfigMutation = useMutation({
    mutationFn: (data: Partial<JobVoiceConfig>) => 
      voiceAgentApi.updateJobConfig(jobId, data),
    onSuccess: () => {
      setSuccessMessage('Job voice agent settings updated successfully');
      queryClient.invalidateQueries({ queryKey: ['job-voice-config', jobId] });
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (error: any) => {
      setErrorMessage(error.response?.data?.detail || 'Failed to update settings');
      setTimeout(() => setErrorMessage(''), 5000);
    },
  });
  
  // Update form data when job config is loaded
  useEffect(() => {
    if (jobConfig) {
      setFormData({
        job_id: jobId,
        use_global_config: jobConfig.use_global_config,
        custom_system_prompt: jobConfig.custom_system_prompt || '',
        custom_questions: jobConfig.custom_questions ? [...jobConfig.custom_questions] : [],
        model: jobConfig.model,
        voice_id: jobConfig.voice_id,
        temperature: jobConfig.temperature,
        recording_enabled: jobConfig.recording_enabled,
      });
    }
  }, [jobConfig, jobId]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSelectChange = (e: any) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSwitchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };
  
  const handleSliderChange = (_: Event, value: number | number[]) => {
    setFormData(prev => ({ ...prev, temperature: value as number }));
  };
  
  const handleAddQuestion = () => {
    if (newQuestion.trim() && formData.custom_questions) {
      setFormData(prev => ({
        ...prev,
        custom_questions: [...(prev.custom_questions || []), newQuestion.trim()]
      }));
      setNewQuestion('');
    }
  };
  
  const handleRemoveQuestion = (index: number) => {
    if (formData.custom_questions) {
      const updatedQuestions = [...formData.custom_questions];
      updatedQuestions.splice(index, 1);
      setFormData(prev => ({ ...prev, custom_questions: updatedQuestions }));
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateConfigMutation.mutate(formData);
  };
  
  const playVoiceSample = (voiceId: string) => {
    const voice = voices?.find(v => v.id === voiceId);
    if (voice?.preview_url) {
      const audio = new Audio(voice.preview_url);
      audio.play();
    }
  };
  
  if (isLoadingConfig || isLoadingModels || isLoadingVoices) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100px">
        <CircularProgress size={24} />
      </Box>
    );
  }
  
  if (configError) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Failed to load job voice agent settings. Please try again later.
      </Alert>
    );
  }
  
  return (
    <Card sx={{ 
      borderRadius: 2,
      bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
      boxShadow: theme.shadows[2],
      mt: 3
    }}>
      <CardContent sx={{ p: 3 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            cursor: 'pointer'
          }}
          onClick={() => setExpanded(!expanded)}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Voice Agent Settings for This Job
          </Typography>
          <IconButton>
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expanded}>
          {successMessage && (
            <Alert severity="success" sx={{ my: 2 }}>
              {successMessage}
            </Alert>
          )}
          
          {errorMessage && (
            <Alert severity="error" sx={{ my: 2 }}>
              {errorMessage}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.use_global_config || false}
                  onChange={handleSwitchChange}
                  name="use_global_config"
                />
              }
              label="Use Global Configuration"
              sx={{ mb: 2 }}
            />
            
            <Collapse in={!formData.use_global_config}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel id="model-label">Voice Model</InputLabel>
                    <Select
                      labelId="model-label"
                      name="model"
                      value={formData.model || ''}
                      onChange={handleSelectChange}
                      label="Voice Model"
                    >
                      {models?.map((model) => (
                        <MenuItem key={model.id} value={model.id}>
                          <Box>
                            <Typography variant="body1">{model.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {model.description}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel id="voice-label">Voice</InputLabel>
                    <Select
                      labelId="voice-label"
                      name="voice_id"
                      value={formData.voice_id || ''}
                      onChange={handleSelectChange}
                      label="Voice"
                    >
                      {voices?.map((voice) => (
                        <MenuItem key={voice.id} value={voice.id}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                            <Box>
                              <Typography variant="body1">{voice.name}</Typography>
                              <Typography variant="caption" color="text.secondary">
                                {voice.language} • {voice.gender || 'Unknown'}
                              </Typography>
                            </Box>
                            {voice.preview_url && (
                              <IconButton 
                                size="small" 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  playVoiceSample(voice.id);
                                }}
                              >
                                <PlayArrowIcon />
                              </IconButton>
                            )}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  
                  <Box sx={{ mb: 3 }}>
                    <Typography gutterBottom>Temperature: {formData.temperature}</Typography>
                    <Slider
                      value={formData.temperature || 0.7}
                      onChange={handleSliderChange}
                      min={0}
                      max={1}
                      step={0.1}
                      valueLabelDisplay="auto"
                      aria-labelledby="temperature-slider"
                    />
                    <Typography variant="caption" color="text.secondary">
                      Lower values make responses more focused and deterministic, higher values make them more creative and varied.
                    </Typography>
                  </Box>
                  
                  <FormControlLabel
                    control={
                      <Switch
                        checked={formData.recording_enabled || false}
                        onChange={handleSwitchChange}
                        name="recording_enabled"
                      />
                    }
                    label="Enable Call Recording"
                    sx={{ mb: 3 }}
                  />
                </Grid>
              </Grid>
            </Collapse>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
              Job-Specific Settings
            </Typography>
            
            <TextField
              label="Custom System Prompt for This Job"
              name="custom_system_prompt"
              value={formData.custom_system_prompt || ''}
              onChange={handleInputChange}
              multiline
              rows={4}
              fullWidth
              sx={{ mb: 3 }}
              helperText="Leave empty to use the global system prompt"
            />
            
            <Typography variant="subtitle2" gutterBottom>
              Custom Questions for This Job
              <Tooltip title="These questions will override the default questions for this job only">
                <IconButton size="small">
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Typography>
            
            <Box sx={{ display: 'flex', mb: 2 }}>
              <TextField
                label="Add a job-specific question"
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                fullWidth
                size="small"
              />
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddQuestion}
                sx={{ ml: 1 }}
                disabled={!newQuestion.trim()}
              >
                Add
              </Button>
            </Box>
            
            <Box sx={{ mb: 3, maxHeight: '200px', overflowY: 'auto' }}>
              {formData.custom_questions?.map((question, index) => (
                <Chip
                  key={index}
                  label={question}
                  onDelete={() => handleRemoveQuestion(index)}
                  sx={{ m: 0.5 }}
                />
              ))}
              {(!formData.custom_questions || formData.custom_questions.length === 0) && (
                <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  No custom questions added. The default questions will be used.
                </Typography>
              )}
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                disabled={updateConfigMutation.isPending}
              >
                {updateConfigMutation.isPending ? 'Saving...' : 'Save Settings'}
              </Button>
            </Box>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
} 