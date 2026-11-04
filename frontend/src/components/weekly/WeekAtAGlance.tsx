import type { DayGlance, WeeklyPage } from '../../api/planner';
import styles from './WeeklyPage.module.css';

interface WeekAtAGlanceProps {
  days: DayGlance[];
  onChange: (patch: Partial<WeeklyPage>) => void;
  onBlur: (patch: Partial<WeeklyPage>) => void;
}

export function WeekAtAGlance({ days, onChange, onBlur }: WeekAtAGlanceProps) {
  function updateDay(index: number, field: keyof DayGlance, value: string) {
    const updated = days.map((d, i) => (i === index ? { ...d, [field]: value } : d));
    onChange({ week_at_a_glance: updated });
  }

  function saveDay() {
    onBlur({ week_at_a_glance: days });
  }

  return (
    <div className={styles.glanceTable} role="table" aria-label="Week at a glance">
      {days.map((day, i) => (
        <div key={day.day} className={styles.glanceRow} role="row">
          <span className={styles.dayLabel} role="cell">
            {day.day.slice(0, 3)}
          </span>
          <input
            type="text"
            className={styles.dayDate}
            value={day.date}
            onChange={(e) => updateDay(i, 'date', e.target.value)}
            onBlur={saveDay}
            aria-label={`${day.day} date`}
          />
          <input
            type="text"
            className={styles.dayText}
            value={day.text}
            onChange={(e) => updateDay(i, 'text', e.target.value)}
            onBlur={saveDay}
            aria-label={`${day.day} summary`}
          />
        </div>
      ))}
    </div>
  );
}
