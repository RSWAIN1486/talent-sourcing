import { useState, useRef, useEffect } from 'react';
import { Box, IconButton, Typography, LinearProgress, Paper } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import StopIcon from '@mui/icons-material/Stop';

interface VoicePreviewProps {
  previewUrl?: string;
  voiceName: string;
}

export default function VoicePreview({ previewUrl, voiceName }: VoicePreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  useEffect(() => {
    // Create audio element
    if (!audioRef.current && previewUrl) {
      audioRef.current = new Audio(previewUrl);
      
      // Add event listeners
      audioRef.current.addEventListener('timeupdate', updateProgress);
      audioRef.current.addEventListener('ended', handleEnded);
    }
    
    // Cleanup on unmount
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.removeEventListener('timeupdate', updateProgress);
        audioRef.current.removeEventListener('ended', handleEnded);
        audioRef.current = null;
      }
    };
  }, [previewUrl]);
  
  const updateProgress = () => {
    if (audioRef.current) {
      const value = (audioRef.current.currentTime / audioRef.current.duration) * 100;
      setProgress(value);
    }
  };
  
  const handleEnded = () => {
    setIsPlaying(false);
    setProgress(0);
  };
  
  const handlePlay = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };
  
  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };
  
  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setProgress(0);
    }
  };
  
  if (!previewUrl) {
    return (
      <Typography variant="body2" color="text.secondary">
        No preview available for this voice
      </Typography>
    );
  }
  
  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 1.5, 
        borderRadius: 2,
        bgcolor: 'background.paper',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        width: '100%'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {!isPlaying ? (
          <IconButton 
            onClick={handlePlay} 
            color="primary" 
            size="small"
            aria-label="play"
          >
            <PlayArrowIcon />
          </IconButton>
        ) : (
          <IconButton 
            onClick={handlePause} 
            color="primary" 
            size="small"
            aria-label="pause"
          >
            <PauseIcon />
          </IconButton>
        )}
        <IconButton 
          onClick={handleStop} 
          color="primary" 
          size="small"
          disabled={!isPlaying && progress === 0}
          aria-label="stop"
        >
          <StopIcon />
        </IconButton>
      </Box>
      
      <Box sx={{ flexGrow: 1 }}>
        <Typography variant="body2" fontWeight={500}>
          {voiceName} Preview
        </Typography>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ 
            mt: 0.5, 
            height: 4, 
            borderRadius: 2 
          }} 
        />
      </Box>
    </Paper>
  );
} 