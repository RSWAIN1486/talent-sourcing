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
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voiceAgentApi, GlobalVoiceConfig, VoiceModel, VoiceInfo } from '../../services/api';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import SaveIcon from '@mui/icons-material/Save';
import VoicePreview from './VoicePreview';

export default function GlobalVoiceSettings() {
  const theme = useTheme();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<Partial<GlobalVoiceConfig>>({
    model: '',
    voice_id: '',
    temperature: 0.7,
    base_system_prompt: '',
    default_questions: [],
    recording_enabled: true,
  });
  
  const [newQuestion, setNewQuestion] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Fetch global config
  const { 
    data: globalConfig, 
    isLoading: isLoadingConfig,
    error: configError 
  } = useQuery({
    queryKey: ['global-voice-config'],
    queryFn: voiceAgentApi.getGlobalConfig,
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
  
  // Update global config mutation
  const updateConfigMutation = useMutation({
    mutationFn: voiceAgentApi.updateGlobalConfig,
    onSuccess: () => {
      setSuccessMessage('Global voice agent settings updated successfully');
      queryClient.invalidateQueries({ queryKey: ['global-voice-config'] });
      setTimeout(() => setSuccessMessage(''), 5000);
    },
    onError: (error: any) => {
      setErrorMessage(error.response?.data?.detail || 'Failed to update settings');
      setTimeout(() => setErrorMessage(''), 5000);
    },
  });
  
  // Update form data when global config is loaded
  useEffect(() => {
    if (globalConfig) {
      setFormData({
        model: globalConfig.model || (models && models.length > 0 ? models[0].id : ''),
        voice_id: globalConfig.voice_id,
        temperature: globalConfig.temperature,
        base_system_prompt: globalConfig.base_system_prompt,
        default_questions: [...globalConfig.default_questions],
        recording_enabled: globalConfig.recording_enabled,
      });
    }
  }, [globalConfig, models]);
  
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
    if (newQuestion.trim() && formData.default_questions) {
      setFormData(prev => ({
        ...prev,
        default_questions: [...(prev.default_questions || []), newQuestion.trim()]
      }));
      setNewQuestion('');
    }
  };
  
  const handleRemoveQuestion = (index: number) => {
    if (formData.default_questions) {
      const updatedQuestions = [...formData.default_questions];
      updatedQuestions.splice(index, 1);
      setFormData(prev => ({ ...prev, default_questions: updatedQuestions }));
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
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    );
  }
  
  if (configError) {
    return (
      <Alert severity="error">
        Failed to load voice agent settings. Please try again later.
      </Alert>
    );
  }
  
  return (
    <Card sx={{ 
      borderRadius: 2,
      bgcolor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'background.paper',
      boxShadow: theme.shadows[2]
    }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
          Global Voice Agent Settings
        </Typography>
        
        {successMessage && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {successMessage}
          </Alert>
        )}
        
        {errorMessage && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {errorMessage}
          </Alert>
        )}
        
        <Box component="form" onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="model-label">Voice Model</InputLabel>
                <Select
                  labelId="model-label"
                  name="model"
                  value={formData.model || ''}
                  onChange={(e) =>
                    handleSelectChange({ target: { name: 'model', value: e.target.value } })
                  }
                  label="Voice Model"
                >
                  {models?.map((model) => (
                    <MenuItem
                      key={model.id ?? model.name}
                      value={model.id ?? model.name}
                    >
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
                <InputLabel id="voice-select-label">Voice</InputLabel>
                <Select
                  labelId="voice-select-label"
                  id="voice-select"
                  value={formData.voice_id}
                  onChange={(e) => handleSelectChange({ target: { name: 'voice_id', value: e.target.value } })}
                  label="Voice"
                >
                  {voices?.map((voice) => (
                    <MenuItem key={voice.id} value={voice.id}>
                      {voice.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {formData.voice_id && (
                <Box sx={{ mt: 2 }}>
                  <VoicePreview 
                    previewUrl={voices?.find(v => v.id === formData.voice_id)?.preview_url} 
                    voiceName={voices?.find(v => v.id === formData.voice_id)?.name || 'Voice'} 
                  />
                </Box>
              )}
              
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
            
            <Grid item xs={12} md={6}>
              <TextField
                label="Base System Prompt"
                name="base_system_prompt"
                value={formData.base_system_prompt || ''}
                onChange={handleInputChange}
                multiline
                rows={6}
                fullWidth
                sx={{ mb: 3 }}
                helperText="Instructions for the AI voice agent that will be used for all calls"
              />
              
              <Typography variant="subtitle2" gutterBottom>
                Default Questions
                <Tooltip title="These questions will be asked in all screening calls unless overridden by job-specific questions">
                  <IconButton size="small">
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Typography>
              
              <Box sx={{ display: 'flex', mb: 2 }}>
                <TextField
                  label="Add a question"
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
                {formData.default_questions?.map((question, index) => (
                  <Chip
                    key={index}
                    label={question}
                    onDelete={() => handleRemoveQuestion(index)}
                    sx={{ m: 0.5 }}
                  />
                ))}
                {(!formData.default_questions || formData.default_questions.length === 0) && (
                  <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                    No default questions added
                  </Typography>
                )}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              
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
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
} 