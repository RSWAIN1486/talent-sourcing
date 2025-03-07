import { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  useTheme, 
  Chip,
  Avatar,
  Divider,
  Paper,
  IconButton,
  Fade,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SpeedIcon from '@mui/icons-material/Speed';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SecurityIcon from '@mui/icons-material/Security';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useColorMode } from '../contexts/ColorModeContext';
import { TestimonialCard } from '../components/TestimonialCard';
import { GradientButton, OutlinedButton } from '../components/Buttons';
import { AIPoweredBadge } from '../components/AIPoweredBadge';

// Styled components
const HeroSection = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  width: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  position: 'relative',
  overflow: 'hidden',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, #0a1929 0%, #1a2027 100%)' 
    : 'linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)',
  padding: theme.spacing(8, 0),
}));

const GradientText = styled(Typography)(({ theme }) => ({
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
    : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  fontWeight: 800,
  letterSpacing: '-0.5px',
  marginBottom: theme.spacing(2),
}));

const FeatureCard = styled(Card)(({ theme }) => ({
  height: '100%',
  borderRadius: '16px',
  boxShadow: theme.palette.mode === 'dark' 
    ? '0 8px 24px rgba(0, 0, 0, 0.2)' 
    : '0 8px 24px rgba(0, 0, 0, 0.05)',
  transition: 'transform 0.3s ease, box-shadow 0.3s ease',
  overflow: 'hidden',
  background: theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)' 
    : '#ffffff',
  '&:hover': {
    transform: 'translateY(-8px)',
    boxShadow: theme.palette.mode === 'dark' 
      ? '0 16px 32px rgba(0, 0, 0, 0.3)' 
      : '0 16px 32px rgba(0, 0, 0, 0.1)',
  }
}));

const StatCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: '16px',
  textAlign: 'center',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  background: theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)' 
    : '#ffffff',
  boxShadow: theme.palette.mode === 'dark' 
    ? '0 8px 24px rgba(0, 0, 0, 0.2)' 
    : '0 8px 24px rgba(0, 0, 0, 0.05)',
  transition: 'transform 0.3s ease',
  '&:hover': {
    transform: 'translateY(-5px)',
  }
}));

const LandingPage = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { toggleColorMode, mode } = useColorMode();
  const [animateFeatures, setAnimateFeatures] = useState(false);
  const [animateStats, setAnimateStats] = useState(false);
  const [animateTestimonials, setAnimateTestimonials] = useState(false);

  useEffect(() => {
    // Trigger animations after component mounts
    setAnimateFeatures(true);
    
    // Delay other animations for a staggered effect
    const statsTimer = setTimeout(() => setAnimateStats(true), 300);
    const testimonialsTimer = setTimeout(() => setAnimateTestimonials(true), 600);
    
    return () => {
      clearTimeout(statsTimer);
      clearTimeout(testimonialsTimer);
    };
  }, []);

  const handleLogin = () => {
    // Check if user is already logged in
    const token = localStorage.getItem('access_token');
    if (token) {
      // If logged in, go directly to jobs
      navigate('/jobs');
    } else {
      // Otherwise go to login page
      navigate('/login');
    }
  };

  const features = [
    {
      title: 'AI-Powered Resume Analysis',
      description: 'Our advanced AI analyzes resumes to extract skills, experience, and qualifications, matching candidates to job requirements with unprecedented accuracy.',
      icon: AutoAwesomeIcon,
      color: '#2196f3'
    },
    {
      title: 'Automated Phone Screening',
      description: 'Save time with AI-driven phone interviews that pre-screen candidates, asking job-specific questions and providing detailed conversation analysis.',
      icon: PeopleAltIcon,
      color: '#4caf50'
    },
    {
      title: 'Intelligent Matching',
      description: 'Our algorithms go beyond keyword matching to understand context, identifying the best candidates based on skills, experience, and potential.',
      icon: SpeedIcon,
      color: '#ff9800'
    },
    {
      title: 'Comprehensive Analytics',
      description: 'Gain insights into your recruitment process with detailed analytics on candidate quality, source effectiveness, and hiring efficiency.',
      icon: AnalyticsIcon,
      color: '#9c27b0'
    }
  ];

  const stats = [
    { value: '75%', label: 'Time Saved', description: 'Reduction in time spent on initial screening' },
    { value: '3x', label: 'More Efficient', description: 'Process more candidates in less time' },
    { value: '60%', label: 'Cost Reduction', description: 'Lower cost per hire compared to traditional methods' },
    { value: '90%', label: 'Accuracy', description: 'In matching candidates to job requirements' }
  ];

  const testimonials = [
    {
      content: "AI Recruiter has transformed our hiring process. We've reduced time-to-hire by 60% while improving the quality of candidates we interview. The AI-powered screening is remarkably accurate.",
      name: "Sarah Johnson",
      position: "HR Director, TechCorp",
      avatar: "SJ"
    },
    {
      content: "The automated phone screening feature has been a game-changer for us. It allows us to evaluate hundreds of candidates quickly without sacrificing the personal touch of a conversation.",
      name: "Michael Chen",
      position: "Talent Acquisition Manager, InnovateCo",
      avatar: "MC"
    },
    {
      content: "We've seen a dramatic improvement in our hiring metrics since implementing AI Recruiter. The platform's ability to identify qualified candidates from our applicant pool is impressive.",
      name: "Jessica Williams",
      position: "Recruiting Lead, GrowthStartup",
      avatar: "JW"
    }
  ];

  return (
    <Box sx={{ 
      width: '100%',
      minHeight: '100vh',
      overflow: 'hidden'
    }}>
      {/* Hero Section */}
      <HeroSection>
        {/* Add theme toggle button */}
        <IconButton
          onClick={toggleColorMode}
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            zIndex: 10,
            bgcolor: theme.palette.mode === 'dark' 
              ? 'rgba(255, 255, 255, 0.05)'
              : 'rgba(0, 0, 0, 0.05)',
            '&:hover': {
              bgcolor: theme.palette.mode === 'dark' 
                ? 'rgba(255, 255, 255, 0.1)'
                : 'rgba(0, 0, 0, 0.1)',
            }
          }}
        >
          {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>

        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ position: 'relative', zIndex: 5 }}>
                <AIPoweredBadge
                  icon={<SmartToyIcon />}
                  label="AI Powered"
                  sx={{ mb: 3 }}
                />
                <GradientText variant="h1" component="h1" sx={{ fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
                  Revolutionize Your Hiring Process
                </GradientText>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    mb: 4, 
                    color: theme.palette.mode === 'dark' ? 'grey.400' : 'grey.700',
                    maxWidth: 550
                  }}
                >
                  Find the perfect candidates faster with AI-powered resume analysis and automated phone screening.
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <GradientButton 
                    variant="contained" 
                    size="large"
                    endIcon={<ArrowForwardIcon />}
                    onClick={() => navigate('/login')}
                  >
                    Get Started
                  </GradientButton>
                  <OutlinedButton 
                    variant="outlined" 
                    size="large"
                    onClick={handleLogin}
                  >
                    Login
                  </OutlinedButton>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ 
                position: 'relative', 
                height: { xs: 450, md: 550, lg: 600 },
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                mt: { xs: 4, md: 0 }
              }}>
                {/* Animated background */}
                <Box sx={{
                  position: 'absolute',
                  width: '80%',
                  height: '80%',
                  background: theme.palette.mode === 'dark' 
                    ? 'radial-gradient(circle, rgba(25, 118, 210, 0.4) 0%, rgba(25, 118, 210, 0.1) 70%, transparent 100%)'
                    : 'radial-gradient(circle, rgba(25, 118, 210, 0.2) 0%, rgba(25, 118, 210, 0.05) 70%, transparent 100%)',
                  borderRadius: '50%',
                  filter: 'blur(40px)',
                  animation: 'pulse 8s infinite ease-in-out',
                  zIndex: 1
                }}/>
                
                {/* Resume card - positioned on the left with negative rotation */}
                <Paper elevation={6} sx={{
                  position: 'absolute',
                  top: '15%',
                  left: '5%',
                  width: 200,
                  height: 260,
                  borderRadius: 2,
                  p: 2,
                  transform: 'rotate(-5deg)',
                  animation: 'float 6s infinite ease-in-out',
                  background: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
                  boxShadow: theme.palette.mode === 'dark' 
                    ? '0 8px 24px rgba(0, 0, 0, 0.3)' 
                    : '0 8px 24px rgba(0, 0, 0, 0.1)',
                  overflow: 'hidden',
                  zIndex: 2
                }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>Resume</Typography>
                    <Chip 
                      label="PDF" 
                      size="small" 
                      sx={{ 
                        height: 20, 
                        fontSize: '0.6rem',
                        bgcolor: theme.palette.error.main,
                        color: '#fff'
                      }}
                    />
                  </Box>
                  
                  <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, mb: 0.5 }}>
                    John Developer
                  </Typography>
                  
                  <Typography variant="caption" sx={{ 
                    display: 'block', 
                    color: theme.palette.primary.main,
                    fontSize: '0.65rem',
                    mb: 1
                  }}>
                    john.dev@example.com
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Typography variant="caption" sx={{ 
                    display: 'block', 
                    fontWeight: 600, 
                    color: 'text.secondary',
                    mb: 0.5
                  }}>
                    Experience
                  </Typography>
                  
                  <Box sx={{ 
                    height: 8, 
                    width: '90%', 
                    bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.300',
                    borderRadius: 1,
                    mb: 0.5
                  }}/>
                  
                  <Box sx={{ 
                    height: 8, 
                    width: '80%', 
                    bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.300',
                    borderRadius: 1,
                    mb: 0.5
                  }}/>
                  
                  <Box sx={{ 
                    height: 8, 
                    width: '60%', 
                    bgcolor: theme.palette.primary.main,
                    borderRadius: 1,
                    mb: 1.5,
                    opacity: 0.7
                  }}/>
                  
                  <Typography variant="caption" sx={{ 
                    display: 'block', 
                    fontWeight: 600, 
                    color: 'text.secondary',
                    mb: 0.5
                  }}>
                    Skills
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    <Chip 
                      label="React" 
                      size="small" 
                      sx={{ height: 16, fontSize: '0.55rem' }}
                    />
                    <Chip 
                      label="Node.js" 
                      size="small" 
                      sx={{ height: 16, fontSize: '0.55rem' }}
                    />
                    <Chip 
                      label="TypeScript" 
                      size="small" 
                      sx={{ height: 16, fontSize: '0.55rem' }}
                    />
                  </Box>
                  
                  <Box sx={{ 
                    height: 8, 
                    width: '70%', 
                    bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.300',
                    borderRadius: 1,
                    mb: 0.5
                  }}/>
                </Paper>
                
                {/* AI analysis card - positioned on the right with positive rotation (opposite to Resume) */}
                <Paper elevation={6} sx={{
                  position: 'absolute',
                  top: '15%',
                  right: '5%',
                  width: 220,
                  height: 240,
                  borderRadius: 2,
                  p: 2,
                  transform: 'rotate(5deg)',
                  animation: 'floatReverse 7s infinite ease-in-out 1s',
                  background: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
                  boxShadow: theme.palette.mode === 'dark' 
                    ? '0 8px 24px rgba(0, 0, 0, 0.3)' 
                    : '0 8px 24px rgba(0, 0, 0, 0.1)',
                  zIndex: 4
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <SmartToyIcon sx={{ color: theme.palette.primary.main, mr: 1, fontSize: 20 }}/>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>AI Analysis</Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>Match Score</Typography>
                    <Box sx={{ 
                      height: 8, 
                      width: '100%', 
                      bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                      borderRadius: 4,
                      position: 'relative',
                      overflow: 'hidden'
                    }}>
                      <Box sx={{ 
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        height: '100%',
                        width: '85%',
                        bgcolor: theme.palette.success.main,
                        borderRadius: 4,
                      }}/>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.success.main }}>85%</Typography>
                    </Box>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>Technical Skills</Typography>
                    <Box sx={{ 
                      height: 8, 
                      width: '100%', 
                      bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
                      borderRadius: 4,
                      position: 'relative',
                      overflow: 'hidden',
                      mb: 0.5
                    }}>
                      <Box sx={{ 
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        height: '100%',
                        width: '90%',
                        bgcolor: theme.palette.primary.main,
                        borderRadius: 4,
                      }}/>
                    </Box>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: theme.palette.primary.main, float: 'right' }}>90%</Typography>
                  </Box>
                  
                  <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>Skills</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    <Chip label="React" size="small" sx={{ height: 20, fontSize: '0.6rem' }}/>
                    <Chip label="TypeScript" size="small" sx={{ height: 20, fontSize: '0.6rem' }}/>
                    <Chip label="Node.js" size="small" sx={{ height: 20, fontSize: '0.6rem' }}/>
                  </Box>
                  
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'center', 
                    mt: 1,
                    bgcolor: theme.palette.success.light,
                    color: theme.palette.success.contrastText,
                    borderRadius: 1,
                    py: 0.5,
                    fontSize: '0.7rem',
                    fontWeight: 600
                  }}>
                    Recommended for Interview
                  </Box>
                </Paper>
                
                {/* Phone call card - positioned at the bottom left */}
                <Paper elevation={6} sx={{
                  position: 'absolute',
                  bottom: '15%',
                  left: '30%',
                  transform: 'translateX(-50%) rotate(2deg)',
                  width: 180,
                  height: 180,
                  borderRadius: 2,
                  p: 2,
                  animation: 'floatHorizontal 7s infinite ease-in-out',
                  background: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
                  boxShadow: theme.palette.mode === 'dark' 
                    ? '0 8px 24px rgba(0, 0, 0, 0.3)' 
                    : '0 8px 24px rgba(0, 0, 0, 0.1)',
                  zIndex: 3
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                    <Box sx={{ 
                      width: 12, 
                      height: 12, 
                      borderRadius: '50%', 
                      bgcolor: theme.palette.success.main,
                      mr: 1
                    }}/>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.75rem' }}>Call in progress</Typography>
                  </Box>
                  
                  <Box sx={{ 
                    height: 40, 
                    bgcolor: theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)',
                    borderRadius: 1,
                    p: 1,
                    mb: 1.5,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-around'
                  }}>
                    <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
                      "Tell me about your experience with React..."
                    </Typography>
                  </Box>
                  
                  <Box sx={{ 
                    height: 40, 
                    bgcolor: theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.2)' : 'rgba(0,0,0,0.05)',
                    borderRadius: 1,
                    p: 1,
                    mb: 1.5,
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-around'
                  }}>
                    <Typography variant="caption" sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
                      "I've worked with React for 3 years..."
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: theme.palette.error.main,
                      color: '#fff',
                      fontSize: '0.8rem'
                    }}>
                      <span>⏹</span>
                    </Box>
                    
                    <Typography variant="caption" sx={{ 
                      display: 'block', 
                      textAlign: 'right', 
                      fontSize: '0.6rem', 
                      color: theme.palette.success.main 
                    }}>
                      5:23 / 10:00
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </HeroSection>

      {/* Features Section */}
      <Box 
        sx={{ 
          py: 12,
          background: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography 
              variant="h2" 
              component="h2" 
              gutterBottom
              sx={{ 
                fontWeight: 700,
                color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.dark',
              }}
            >
              Powerful Features
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                maxWidth: 700,
                mx: 'auto',
                color: theme.palette.mode === 'dark' ? 'grey.400' : 'grey.700',
              }}
            >
              Our AI-powered platform streamlines every step of the recruitment process
            </Typography>
          </Box>
          
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Fade 
                  in={animateFeatures} 
                  timeout={1000} 
                  style={{ transitionDelay: `${index * 100}ms` }}
                >
                  <FeatureCard>
                    <CardContent sx={{ p: 3 }}>
                      <Box 
                        sx={{ 
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 60,
                          height: 60,
                          borderRadius: '50%',
                          mb: 2,
                          background: theme.palette.mode === 'dark' 
                            ? 'rgba(255, 255, 255, 0.05)' 
                            : 'rgba(0, 0, 0, 0.03)',
                        }}
                      >
                        <feature.icon 
                          sx={{ 
                            fontSize: 30, 
                            color: feature.color,
                          }} 
                        />
                      </Box>
                      <Typography 
                        variant="h6" 
                        component="h3" 
                        gutterBottom
                        sx={{ fontWeight: 600 }}
                      >
                        {feature.title}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{ lineHeight: 1.7 }}
                      >
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </FeatureCard>
                </Fade>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box 
        sx={{ 
          py: 12,
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, #0a1929 0%, #1a2027 100%)' 
            : 'linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            {stats.map((stat, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Fade 
                  in={animateStats} 
                  timeout={1000} 
                  style={{ transitionDelay: `${index * 100}ms` }}
                >
                  <StatCard>
                    <Typography 
                      variant="h2" 
                      component="div" 
                      gutterBottom
                      sx={{ 
                        fontWeight: 700,
                        color: theme.palette.primary.main,
                      }}
                    >
                      {stat.value}
                    </Typography>
                    <Typography 
                      variant="h6" 
                      component="div" 
                      gutterBottom
                      sx={{ fontWeight: 600 }}
                    >
                      {stat.label}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                    >
                      {stat.description}
                    </Typography>
                  </StatCard>
                </Fade>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box 
        sx={{ 
          py: 12,
          background: theme.palette.mode === 'dark' ? '#1a2027' : '#fff',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: 'center', mb: 8 }}>
            <Typography 
              variant="h3" 
              component="h2" 
              gutterBottom
              sx={{ 
                fontWeight: 700,
                color: theme.palette.mode === 'dark' ? 'primary.light' : 'primary.dark',
              }}
            >
              What Our Clients Say
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                maxWidth: 700,
                mx: 'auto',
                color: theme.palette.mode === 'dark' ? 'grey.400' : 'grey.700',
              }}
            >
              Hear from the companies that have transformed their hiring process
            </Typography>
          </Box>
          
          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Fade 
                  in={animateTestimonials} 
                  timeout={1000} 
                  style={{ transitionDelay: `${index * 100}ms` }}
                >
                  <TestimonialCard>
                    <CardContent sx={{ p: 3 }}>
                      <Typography 
                        variant="body1" 
                        paragraph
                        sx={{ 
                          mb: 4,
                          color: theme.palette.mode === 'dark' ? 'grey.300' : 'grey.800',
                          lineHeight: 1.7,
                          fontStyle: 'italic'
                        }}
                      >
                        "{testimonial.content}"
                      </Typography>
                      <Divider sx={{ mb: 3 }} />
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar 
                          sx={{ 
                            bgcolor: theme.palette.primary.main,
                            color: '#fff',
                            fontWeight: 600,
                            mr: 2
                          }}
                        >
                          {testimonial.avatar}
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                            {testimonial.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {testimonial.position}
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </TestimonialCard>
                </Fade>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box 
        sx={{ 
          py: 12,
          background: theme.palette.mode === 'dark' 
            ? 'linear-gradient(135deg, rgba(10, 25, 41, 0.95) 0%, rgba(26, 32, 39, 0.95) 100%), url(/images/cta-bg.jpg) no-repeat center center' 
            : 'linear-gradient(135deg, rgba(25, 118, 210, 0.95) 0%, rgba(33, 150, 243, 0.95) 100%), url(/images/cta-bg.jpg) no-repeat center center',
          backgroundSize: 'cover',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Container maxWidth="md">
          <Box 
            sx={{ 
              textAlign: 'center',
              position: 'relative',
              zIndex: 2,
            }}
          >
            <AIPoweredBadge
              icon={<SmartToyIcon />}
              label="AI Powered"
              sx={{ mb: 3 }}
            />
            <Typography 
              variant="h2" 
              component="h2" 
              gutterBottom
              sx={{ 
                fontWeight: 700,
                color: '#fff',
                mb: 3,
              }}
            >
              Ready to Transform Your Hiring?
            </Typography>
            <Typography 
              variant="h6" 
              sx={{ 
                maxWidth: 700,
                mx: 'auto',
                color: 'rgba(255, 255, 255, 0.9)',
                mb: 5,
              }}
            >
              Join thousands of companies using AI Recruiter to find the best talent faster and more efficiently.
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
              <GradientButton 
                variant="contained" 
                size="large"
                onClick={handleLogin}
                sx={{ 
                  background: '#fff',
                  color: theme.palette.mode === 'dark' ? '#1a2027' : '#1976d2',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.9)',
                  }
                }}
              >
                Get Started Now
              </GradientButton>
              <OutlinedButton 
                variant="outlined" 
                size="large"
                onClick={handleLogin}
                sx={{ 
                  borderColor: '#fff',
                  color: '#fff',
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.9)',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  }
                }}
              >
                Login
              </OutlinedButton>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          py: 6,
          bgcolor: theme.palette.mode === 'dark' ? '#0a1929' : '#f5f5f5',
          color: theme.palette.mode === 'dark' ? 'grey.400' : 'grey.700',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography 
                  variant="h6" 
                  component="div" 
                  sx={{ 
                    mr: 1,
                    background: theme.palette.mode === 'dark'
                      ? 'linear-gradient(45deg, #90caf9 30%, #64b5f6 90%)'
                      : 'linear-gradient(45deg, #1976d2 30%, #2196f3 90%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 600,
                  }}
                >
                  AI Recruiter
                </Typography>
                <AIPoweredBadge
                  icon={<SmartToyIcon />}
                  label="AI Powered"
                  size="small"
                />
              </Box>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Transforming recruitment with artificial intelligence.
                Find the best talent faster and more efficiently.
              </Typography>
              <Typography variant="body2">
                © {new Date().getFullYear()} AI Recruiter. All rights reserved.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                Product
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Features</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Pricing</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Case Studies</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Testimonials</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                Company
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>About Us</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Careers</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Blog</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Contact</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                Resources
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Documentation</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Help Center</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>API</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Community</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                Legal
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Privacy Policy</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Terms of Service</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Security</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>Compliance</Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage; 