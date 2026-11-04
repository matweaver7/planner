import styles from './shared.module.css';

interface SectionHeaderProps {
  label: string;
}

export function SectionHeader({ label }: SectionHeaderProps) {
  return <div className={styles.sectionHeader}>{label}</div>;
}
