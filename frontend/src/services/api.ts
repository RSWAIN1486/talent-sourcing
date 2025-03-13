import axios, { AxiosProgressEvent } from 'axios';

// Get the API URL from environment variables, fallback to localhost for development
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

console.log('Using API URL:', API_URL); // For debugging

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CORS with credentials
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface Job {
  id: string;  // MongoDB ObjectId as string
  title: string;
  description: string;
  responsibilities: string;
  requirements: string;
  created_at: string;
  updated_at: string;
  total_candidates: number;
  resume_screened: number;
  phone_screened: number;
  created_by_id?: string;  // MongoDB ObjectId as string
}

export interface Candidate {
  id: string;  // MongoDB ObjectId as string
  job_id: string;  // MongoDB ObjectId as string
  name: string;
  email: string;
  phone?: string | null;
  location?: string | null;
  resume_file_id: string;  // Changed from resume_path
  skills: Record<string, number>;
  resume_score: number;
  screening_score?: number | null;
  screening_summary?: string | null;
  screening_in_progress?: boolean;
  call_transcript?: string | null;
  notice_period?: string | null;
  current_compensation?: string | null;
  expected_compensation?: string | null;
  created_by_id?: string;  // Added to match backend
  created_at: string;
  updated_at: string;
}

export interface JobStats {
  total_jobs: number;
  total_candidates: number;
  resume_screened: number;
  phone_screened: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Voice Agent Types
export interface VoiceModel {
  id: string;
  name: string;
  description: string;
}

export interface VoiceInfo {
  id: string;
  name: string;
  language: string;
  gender?: string;
  description?: string;
  preview_url?: string;
}

export interface GlobalVoiceConfig {
  model: string;
  voice_id: string;
  temperature: number;
  base_system_prompt: string;
  default_questions: string[];
  recording_enabled: boolean;
  created_at?: string;
  updated_at?: string;
  created_by_id?: string;
}

export interface JobVoiceConfig {
  job_id: string;
  custom_system_prompt?: string;
  custom_questions?: string[];
  use_global_config: boolean;
  model?: string;
  voice_id?: string;
  temperature?: number;
  recording_enabled?: boolean;
  created_at?: string;
  updated_at?: string;
  created_by_id?: string;
}

// API functions
export const jobsApi = {
  // Jobs
  getJobs: () => api.get<Job[]>('/jobs').then(res => res.data),
  getJob: (id: string) => api.get<Job>(`/jobs/${id}`).then(res => res.data),
  createJob: async (data: Omit<Job, 'id' | 'created_at' | 'updated_at' | 'total_candidates' | 'resume_screened' | 'phone_screened' | 'created_by_id'>) => {
    try {
      console.log('createJob - Input data:', data);
      const payload = {
        title: data.title.trim(),
        description: data.description.trim(),
        responsibilities: data.responsibilities.trim(),
        requirements: data.requirements.trim()
      };
      console.log('createJob - Prepared payload:', payload);
      console.log('createJob - Request headers:', api.defaults.headers);
      const response = await api.post<Job>('/jobs', payload);
      console.log('createJob - Response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('createJob - Error details:', {
        error,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers
      });
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Failed to create job');
    }
  },
  updateJob: (id: string, data: Partial<Job>) =>
    api.put<Job>(`/jobs/${id}`, data).then(res => res.data),
  deleteJob: (id: string) => api.delete(`/jobs/${id}`),
  getJobStats: () => api.get<JobStats>('/jobs/stats').then(res => res.data),
  syncJobCandidates: (id: string) => 
    api.post<Job>(`/jobs/${id}/sync-candidates`).then(res => res.data),

  // Candidates
  getCandidates: (jobId: string) =>
    api.get<Candidate[]>(`/candidates/${jobId}/candidates`).then(res => res.data),
  getCandidate: (jobId: string, candidateId: string) =>
    api.get<Candidate>(`/candidates/${jobId}/candidates/${candidateId}`).then(res => res.data),
  createCandidate: (jobId: string, formData: FormData, onProgress?: (progressEvent: AxiosProgressEvent) => void) =>
    api.post<Candidate>(`/candidates/${jobId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    }).then(res => res.data),
  updateCandidate: (jobId: string, candidateId: string, data: Partial<Candidate>) =>
    api.put<Candidate>(`/candidates/${jobId}/${candidateId}`, data).then(res => res.data),
  deleteCandidate: (jobId: string, candidateId: string) => 
    api.delete(`/candidates/${jobId}/candidates/${candidateId}`),
  downloadResume: async (jobId: string, candidateId: string) => {
    try {
      console.log(`Initiating download for job: ${jobId}, candidate: ${candidateId}`);
      
      const response = await api.get(`/candidates/${jobId}/candidates/${candidateId}/resume`, {
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf',
        },
      });
      
      console.log('Response headers:', response.headers);
      console.log('Response type:', response.data.type);
      console.log('Response size:', response.data.size);
      
      // Get filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      console.log('Content-Disposition header:', contentDisposition);
      
      let filename = `resume.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
          console.log('Extracted filename:', filename);
        } else {
          console.log('No filename found in Content-Disposition header');
        }
      } else {
        console.log('No Content-Disposition header found');
      }

      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      console.log('Created blob:', {
        type: blob.type,
        size: blob.size
      });
      
      const url = window.URL.createObjectURL(blob);
      console.log('Created blob URL:', url);
      
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      
      console.log('Initiating download with:', {
        filename,
        blobType: blob.type,
        blobSize: blob.size
      });
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('Download process completed');
    } catch (error: any) {
      console.error('Error downloading resume:', error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          headers: error.response.headers,
          data: error.response.data
        });
      }
      throw error;
    }
  },
  screenCandidate: async (jobId: string, candidateId: string) => {
    try {
      console.log(`Initiating screening for job: ${jobId}, candidate: ${candidateId}`);
      const response = await api.post<Candidate>(
        `/candidates/${jobId}/candidates/${candidateId}/screen`
      );
      return response.data;
    } catch (error: any) {
      console.error('Error initiating screening:', error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          headers: error.response.headers,
          data: error.response.data
        });
      }
      throw error;
    }
  },
  
  // Voice screening
  voiceScreenCandidate: async (jobId: string, candidateId: string) => {
    try {
      console.log(`Initiating voice screening for job: ${jobId}, candidate: ${candidateId}`);
      const response = await api.post<{status: string, call_id: string}>(
        `/candidates/${jobId}/${candidateId}/voice-screen`
      );
      return response.data;
    } catch (error: any) {
      console.error('Error initiating voice screening:', error);
      if (error.response) {
        console.error('Error response:', {
          status: error.response.status,
          headers: error.response.headers,
          data: error.response.data
        });
      }
      throw error;
    }
  },
};

// Auth functions
export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<AuthResponse>('/auth/login', new URLSearchParams({
      username: credentials.username,
      password: credentials.password
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }).then(res => {
      localStorage.setItem('access_token', res.data.access_token);
      return res.data;
    }),
  
  register: (data: RegisterData) =>
    api.post('/auth/register', data).then(res => res.data),

  logout: () => {
    localStorage.removeItem('access_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Voice Agent API
export const voiceAgentApi = {
  getGlobalConfig: async (): Promise<GlobalVoiceConfig> => {
    const response = await api.get('/voice-agent/global-config');
    return response.data;
  },
  
  updateGlobalConfig: async (config: Partial<GlobalVoiceConfig>): Promise<GlobalVoiceConfig> => {
    const response = await api.put('/voice-agent/global-config', config);
    return response.data;
  },
  
  getJobConfig: async (jobId: string): Promise<JobVoiceConfig> => {
    const response = await api.get(`/voice-agent/job-config/${jobId}`);
    return response.data;
  },
  
  updateJobConfig: async (jobId: string, config: Partial<JobVoiceConfig>): Promise<JobVoiceConfig> => {
    const response = await api.put(`/voice-agent/job-config/${jobId}`, config);
    return response.data;
  },
  
  getVoices: async (): Promise<VoiceInfo[]> => {
    const response = await api.get('/voice-agent/voices');
    return response.data;
  },
  
  getModels: async (): Promise<VoiceModel[]> => {
    const response = await api.get('/voice-agent/models');
    return response.data;
  }
};

export default api; 