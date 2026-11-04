import { SectionHeader } from '../shared/SectionHeader';
import { RuledField } from '../shared/RuledField';
import { useMonthlyPage } from '../../hooks/useMonthlyPage';
import type { MonthlyPage as MonthlyPageData } from '../../api/planner';
import styles from './MonthlyPage.module.css';

const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

interface MonthlyPageProps {
  year: number;
  month: number;
}

export function MonthlyPage({ year, month }: MonthlyPageProps) {
  const { page, saved, save, update } = useMonthlyPage(year, month);

  if (!page) {
    return <div style={{ padding: '24px', color: 'var(--color-text-muted)' }}>Loading…</div>;
  }

  function field(label: string, key: keyof MonthlyPageData) {
    const value = String(page![key] ?? '');
    return (
      <section key={key}>
        <SectionHeader label={label} />
        <RuledField
          rows={3}
          value={value}
          onChange={(e) => update({ [key]: e.target.value } as Partial<MonthlyPageData>)}
          onBlur={() => save({ [key]: value } as Partial<MonthlyPageData>)}
          aria-label={label}
        />
      </section>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <span className={styles.pageTitle}>Monthly Goals</span>
        <span>{MONTH_NAMES[month]} {year}</span>
      </div>

      <div className={styles.monthOfRow}>
        <span className={styles.monthOfLabel}>Month of</span>
        <span>{MONTH_NAMES[month]} {year}</span>
      </div>

      {field('Study Topic', 'study_topic')}
      {field('Educational Goal', 'educational_goal')}
      {field('Exercise Goal', 'exercise_goal')}
      {field('Career Goal', 'career_goal')}
      {field('Other Goals', 'other_goals')}

      {saved && (
        <div className={styles.savedIndicator} role="status">
          Saved
        </div>
      )}
    </div>
  );
}
