import { useParams, Navigate } from 'react-router-dom';
import { PageShell } from '../components/layout/PageShell';
import { MonthlyPage } from '../components/monthly/MonthlyPage';

export function MonthlyView() {
  const { year, month } = useParams<{ year: string; month: string }>();

  if (!year || !month) return <Navigate to="/" replace />;

  const y = parseInt(year);
  const m = parseInt(month);

  if (isNaN(y) || isNaN(m)) return <Navigate to="/" replace />;

  return (
    <PageShell pageType="monthly">
      <MonthlyPage year={y} month={m} />
    </PageShell>
  );
}
