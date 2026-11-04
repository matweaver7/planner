import { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import { login } from '../api/auth';
import { useAuth } from '../hooks/useAuth';
import styles from './AuthPage.module.css';

export function LoginPage() {
  const { token, setAuth } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Already authenticated — redirect
  if (token) return <Navigate to={`/daily/${todayDate()}`} replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(username, password);
      // Extract user_id from the JWT payload (base64 middle segment)
      const payload = JSON.parse(atob(data.token.split('.')[1]));
      setAuth(data.token, payload.sub as string);
      navigate(`/daily/${todayDate()}`);
    } catch {
      setError('Invalid username or password.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Planner</h1>
        <form onSubmit={handleSubmit} noValidate>
          <div className={styles.field}>
            <label htmlFor="username" className={styles.label}>
              Username
            </label>
            <input
              id="username"
              type="text"
              className={styles.input}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              autoFocus
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              Password
            </label>
            <input
              id="password"
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}
          <button type="submit" className={styles.button} disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className={styles.link}>
          No account? <Link to="/register">Create one</Link>
        </p>
      </div>
    </div>
  );
}

function todayDate(): string {
  return new Date().toISOString().slice(0, 10);
}
