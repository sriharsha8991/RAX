import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import ProtectedRoute from '@/components/layout/ProtectedRoute';
import AppShell from '@/components/layout/AppShell';
import { ToastProvider } from '@/components/ui/Toast';
import { PageSpinner } from '@/components/ui/Spinner';

// Lazy-loaded pages — only downloaded when navigated to
const LandingPage = lazy(() => import('@/pages/LandingPage'));
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const JobListPage = lazy(() => import('@/pages/JobListPage'));
const CreateJobPage = lazy(() => import('@/pages/CreateJobPage'));
const JobDetailPage = lazy(() => import('@/pages/JobDetailPage'));
const UploadPage = lazy(() => import('@/pages/UploadPage'));
const CandidateListPage = lazy(() => import('@/pages/CandidateListPage'));
const CandidateDetailPage = lazy(() => import('@/pages/CandidateDetailPage'));
const FeedbackPage = lazy(() => import('@/pages/FeedbackPage'));

function App() {
  const hydrate = useAuthStore((s) => s.hydrate);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <BrowserRouter>
      <ToastProvider>
        <Suspense fallback={<div className="flex items-center justify-center h-screen"><PageSpinner label="Loading RAX…" /></div>}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected app routes */}
            <Route path="/app" element={<ProtectedRoute />}>
              <Route element={<AppShell />}>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="jobs" element={<JobListPage />} />
                <Route path="jobs/new" element={<CreateJobPage />} />
                <Route path="jobs/:id" element={<JobDetailPage />} />
                <Route path="upload/:jobId" element={<UploadPage />} />
                <Route path="candidates/:jobId" element={<CandidateListPage />} />
                <Route path="candidates/:jobId/:resumeId" element={<CandidateDetailPage />} />
                <Route path="feedback/:id" element={<FeedbackPage />} />
              </Route>
            </Route>

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
