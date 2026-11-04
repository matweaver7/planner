import { SectionHeader } from '../shared/SectionHeader';
import { RuledField } from '../shared/RuledField';
import { WeekAtAGlance } from './WeekAtAGlance';
import { useWeeklyPage } from '../../hooks/useWeeklyPage';
import type { WeeklyPage as WeeklyPageData } from '../../api/planner';
import styles from './WeeklyPage.module.css';

interface WeeklyPageProps {
  year: number;
  week: number;
}

export function WeeklyPage({ year, week }: WeeklyPageProps) {
  const { page, saved, save, update } = useWeeklyPage(year, week);

  if (!page) {
    return <div style={{ padding: '24px', color: 'var(--color-text-muted)' }}>Loading…</div>;
  }

  function field(
    label: string,
    key: keyof WeeklyPageData,
  ) {
    const value = String(page![key] ?? '');
    return (
      <section key={key}>
        <SectionHeader label={label} />
        <RuledField
          rows={3}
          value={value}
          onChange={(e) => update({ [key]: e.target.value } as Partial<WeeklyPageData>)}
          onBlur={() => save({ [key]: value } as Partial<WeeklyPageData>)}
          aria-label={label}
        />
      </section>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.pageHeader}>
        <span className={styles.pageTitle}>Weekly Goals</span>
        <span>Week {week}, {year}</span>
      </div>

      <div className={styles.weekOfRow}>
        <span className={styles.weekOfLabel}>Week of</span>
        <input
          type="text"
          className={styles.weekOfInput}
          value={page.week_of_date}
          onChange={(e) => update({ week_of_date: e.target.value })}
          onBlur={() => save({ week_of_date: page.week_of_date })}
          aria-label="Week of date"
        />
      </div>

      {field('Study Topic', 'study_topic')}
      {field('Educational Goal', 'educational_goal')}
      {field('Exercise Goal', 'exercise_goal')}
      {field('Career Goal', 'career_goal')}
      {field('Other Goals', 'other_goals')}

      <SectionHeader label="Week at a Glance" />
      <WeekAtAGlance
        days={page.week_at_a_glance}
        onChange={update}
        onBlur={save}
      />

      {saved && (
        <div className={styles.savedIndicator} role="status">
          Saved
        </div>
      )}
    </div>
  );
}
