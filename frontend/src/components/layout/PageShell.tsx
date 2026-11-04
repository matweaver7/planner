import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { logout } from '../../api/auth';
import styles from './PageShell.module.css';

interface PageShellProps {
  children: React.ReactNode;
  pageType: 'daily' | 'weekly' | 'monthly';
}

export function PageShell({ children, pageType }: PageShellProps) {
  const navigate = useNavigate();
  const { token } = useAuth();
  const params = useParams();

  async function handleLogout() {
    if (token) {
      try {
        await logout(token);
      } catch {
        // ignore logout errors
      }
    }
    navigate('/login');
  }

  function navigateToPrev() {
    const next = getAdjacentPath(pageType, params, -1);
    if (next) navigate(next);
  }

  function navigateToNext() {
    const next = getAdjacentPath(pageType, params, 1);
    if (next) navigate(next);
  }

  function switchToDaily() {
    navigate(`/daily/${todayDate()}`);
  }

  function switchToWeekly() {
    const [year, week] = currentIsoWeek();
    navigate(`/weekly/${year}/${week}`);
  }

  function switchToMonthly() {
    const d = new Date();
    navigate(`/monthly/${d.getFullYear()}/${d.getMonth() + 1}`);
  }

  return (
    <div className={styles.shell}>
      <nav className={styles.nav} aria-label="Planner navigation">
        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${pageType === 'daily' ? styles.active : ''}`}
            onClick={switchToDaily}
          >
            Daily
          </button>
          <button
            className={`${styles.tab} ${pageType === 'weekly' ? styles.active : ''}`}
            onClick={switchToWeekly}
          >
            Weekly
          </button>
          <button
            className={`${styles.tab} ${pageType === 'monthly' ? styles.active : ''}`}
            onClick={switchToMonthly}
          >
            Monthly
          </button>
        </div>

        <div className={styles.dateNav}>
          <button className={styles.navBtn} onClick={navigateToPrev} aria-label="Previous">
            ‹
          </button>
          <span className={styles.dateLabel}>{currentLabel(pageType, params)}</span>
          <button className={styles.navBtn} onClick={navigateToNext} aria-label="Next">
            ›
          </button>
        </div>

        <button className={styles.logoutBtn} onClick={handleLogout}>
          Log out
        </button>
      </nav>
      <main className={styles.content}>{children}</main>
    </div>
  );
}

function todayDate(): string {
  return new Date().toISOString().slice(0, 10);
}

function currentIsoWeek(): [number, number] {
  const d = new Date();
  const dayOfWeek = d.getDay() || 7;
  d.setDate(d.getDate() + 4 - dayOfWeek);
  const yearStart = new Date(d.getFullYear(), 0, 1);
  const week = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return [d.getFullYear(), week];
}

function getAdjacentPath(
  type: 'daily' | 'weekly' | 'monthly',
  params: Record<string, string | undefined>,
  dir: 1 | -1,
): string | null {
  if (type === 'daily' && params.date) {
    const d = new Date(params.date + 'T00:00:00');
    d.setDate(d.getDate() + dir);
    return `/daily/${d.toISOString().slice(0, 10)}`;
  }
  if (type === 'weekly' && params.year && params.week) {
    const year = parseInt(params.year);
    const week = parseInt(params.week) + dir;
    if (week < 1) return `/weekly/${year - 1}/52`;
    if (week > 52) return `/weekly/${year + 1}/1`;
    return `/weekly/${year}/${week}`;
  }
  if (type === 'monthly' && params.year && params.month) {
    const year = parseInt(params.year);
    const month = parseInt(params.month) + dir;
    if (month < 1) return `/monthly/${year - 1}/12`;
    if (month > 12) return `/monthly/${year + 1}/1`;
    return `/monthly/${year}/${month}`;
  }
  return null;
}

function currentLabel(
  type: 'daily' | 'weekly' | 'monthly',
  params: Record<string, string | undefined>,
): string {
  if (type === 'daily' && params.date) return params.date;
  if (type === 'weekly' && params.year && params.week)
    return `Week ${params.week}, ${params.year}`;
  if (type === 'monthly' && params.year && params.month)
    return `${params.year}-${String(params.month).padStart(2, '0')}`;
  return '';
}
