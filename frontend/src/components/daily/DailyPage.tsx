import { SectionHeader } from '../shared/SectionHeader';
import { TimeBlock } from './TimeBlock';
import { NotesSidebar } from './NotesSidebar';
import { useDailyPage } from '../../hooks/useDailyPage';
import type { TimeBlock as TimeBlockData } from '../../api/planner';
import styles from './DailyPage.module.css';

interface DailyPageProps {
  date: string;
}

export function DailyPage({ date }: DailyPageProps) {
  const { page, saved, save, update } = useDailyPage(date);

  if (!page) {
    return <div style={{ padding: '24px', color: 'var(--color-text-muted)' }}>Loading…</div>;
  }

  const formattedDate = formatDate(date);

  function handleTimeBlockChange(index: number, text: string) {
    const timeBlocks = page!.time_blocks.map((block, i) =>
      i === index ? { ...block, text } : block,
    );
    update({ time_blocks: timeBlocks });
  }

  function handleTimeBlockBlur() {
    save({ time_blocks: page!.time_blocks });
  }

  return (
    <div className={styles.page}>
      {/* Left column: schedule */}
      <div className={styles.leftColumn}>
        <div className={styles.pageHeader}>
          <span className={styles.pageTitle}>Daily Plan</span>
          <span className={styles.pageDate}>{formattedDate}</span>
        </div>
        <SectionHeader label="Schedule" />
        <ul className={styles.timeBlockList}>
          {page.time_blocks.map((block: TimeBlockData, i: number) => (
            <TimeBlock
              key={block.time}
              time={block.time}
              text={block.text}
              onChange={(value) => handleTimeBlockChange(i, value)}
              onBlur={handleTimeBlockBlur}
            />
          ))}
        </ul>
      </div>

      {/* Right column: notes */}
      <div className={styles.rightColumn}>
        <div className={styles.pageHeader}>
          <span className={styles.pageTitle}>Notes</span>
          <span className={styles.pageDate}>{formattedDate}</span>
        </div>
        <NotesSidebar
          page={page}
          onChange={update}
          onBlur={save}
        />
      </div>

      {saved && (
        <div className={styles.savedIndicator} role="status">
          Saved
        </div>
      )}
    </div>
  );
}

function formatDate(iso: string): string {
  const d = new Date(iso + 'T00:00:00');
  return d.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
}
