import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Login from './pages/Login';
import Jobs from './pages/Jobs';
import JobDetails from './pages/JobDetails';
import Statistics from './pages/Statistics';
import LandingPage from './pages/LandingPage';
import { ColorModeProvider } from './contexts/ColorModeContext';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Protected Route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ColorModeProvider>
        <Router>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              {/* Redirect root to jobs */}
              <Route path="/" element={<Navigate to="/jobs" replace />} />
              
              {/* Main routes without dashboard prefix */}
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/jobs/:id" element={<JobDetails />} />
              <Route path="/stats" element={<Statistics />} />
              
              {/* Keep dashboard routes for backward compatibility */}
              <Route path="/dashboard" element={<Navigate to="/jobs" replace />} />
              <Route path="/dashboard/jobs" element={<Navigate to="/jobs" replace />} />
              <Route path="/dashboard/jobs/:id" element={<Navigate to="/jobs/:id" replace />} />
              <Route path="/dashboard/stats" element={<Navigate to="/stats" replace />} />
            </Route>
          </Routes>
        </Router>
      </ColorModeProvider>
    </QueryClientProvider>
  );
}

export default App;
