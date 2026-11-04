import { useParams, Navigate } from 'react-router-dom';
import { PageShell } from '../components/layout/PageShell';
import { WeeklyPage } from '../components/weekly/WeeklyPage';

export function WeeklyView() {
  const { year, week } = useParams<{ year: string; week: string }>();

  if (!year || !week) return <Navigate to="/" replace />;

  const y = parseInt(year);
  const w = parseInt(week);

  if (isNaN(y) || isNaN(w)) return <Navigate to="/" replace />;

  return (
    <PageShell pageType="weekly">
      <WeeklyPage year={y} week={w} />
    </PageShell>
  );
}
