import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Landing } from './components/Landing';
import { SignIn } from './components/SignIn';
import { SignUp } from './components/SignUp';
import { Chat } from './components/Chat';
import { MainHub } from './components/MainHub';
import { DataAnalysisPage, ReportPage, PresentationPage, DashboardPage } from './components/AgentPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return <>{children}</>;
};

// Public Route - redirects to hub if already logged in
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/hub" replace />;
  }

  return <>{children}</>;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={
        <PublicRoute>
          <Landing />
        </PublicRoute>
      } />
      <Route path="/signin" element={
        <PublicRoute>
          <SignIn />
        </PublicRoute>
      } />
      <Route path="/signup" element={
        <PublicRoute>
          <SignUp />
        </PublicRoute>
      } />

      {/* Protected Routes */}
      <Route path="/hub" element={
        <ProtectedRoute>
          <MainHub />
        </ProtectedRoute>
      } />
      <Route path="/chat" element={
        <ProtectedRoute>
          <Chat />
        </ProtectedRoute>
      } />
      <Route path="/analysis" element={
        <ProtectedRoute>
          <DataAnalysisPage />
        </ProtectedRoute>
      } />
      <Route path="/report" element={
        <ProtectedRoute>
          <ReportPage />
        </ProtectedRoute>
      } />
      <Route path="/presentation" element={
        <ProtectedRoute>
          <PresentationPage />
        </ProtectedRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      } />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;
