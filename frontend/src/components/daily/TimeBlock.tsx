import styles from './TimeBlock.module.css';

interface TimeBlockProps {
  time: string;
  text: string;
  onChange: (value: string) => void;
  onBlur: () => void;
}

export function TimeBlock({ time, text, onChange, onBlur }: TimeBlockProps) {
  return (
    <li className={styles.row}>
      <span className={styles.timeLabel}>{time}</span>
      <input
        type="text"
        className={styles.input}
        value={text}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        aria-label={`Time block ${time}`}
      />
    </li>
  );
}
