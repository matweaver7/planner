import { useParams, Navigate } from 'react-router-dom';
import { PageShell } from '../components/layout/PageShell';
import { DailyPage } from '../components/daily/DailyPage';

export function DailyView() {
  const { date } = useParams<{ date: string }>();

  if (!date) return <Navigate to={`/daily/${todayDate()}`} replace />;

  return (
    <PageShell pageType="daily">
      <DailyPage date={date} />
    </PageShell>
  );
}

function todayDate(): string {
  return new Date().toISOString().slice(0, 10);
}
