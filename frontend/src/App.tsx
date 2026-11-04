import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext, useAuthState, useAuth } from './hooks/useAuth';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DailyView } from './pages/DailyView';
import { WeeklyView } from './pages/WeeklyView';
import { MonthlyView } from './pages/MonthlyView';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export function App() {
  const auth = useAuthState();

  return (
    <AuthContext.Provider value={auth}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <Navigate to={`/daily/${todayDate()}`} replace />
            </RequireAuth>
          }
        />
        <Route
          path="/daily/:date"
          element={
            <RequireAuth>
              <DailyView />
            </RequireAuth>
          }
        />
        <Route
          path="/weekly/:year/:week"
          element={
            <RequireAuth>
              <WeeklyView />
            </RequireAuth>
          }
        />
        <Route
          path="/monthly/:year/:month"
          element={
            <RequireAuth>
              <MonthlyView />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthContext.Provider>
  );
}

function todayDate(): string {
  return new Date().toISOString().slice(0, 10);
}
