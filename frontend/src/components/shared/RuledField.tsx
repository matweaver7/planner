import { useRef, useEffect } from 'react';
import styles from './shared.module.css';

interface RuledFieldProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  rows?: number;
}

export function RuledField({ rows = 4, onChange, ...props }: RuledFieldProps) {
  const ref = useRef<HTMLTextAreaElement>(null);

  // Auto-resize to fit content while respecting minimum rows
  function resize() {
    const el = ref.current;
    if (!el) return;
    el.style.height = 'auto';
    const minHeight = (rows + 1) * 26; // 26px per ruled line
    el.style.height = `${Math.max(el.scrollHeight, minHeight)}px`;
  }

  useEffect(() => {
    resize();
  });

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    resize();
    onChange?.(e);
  }

  return (
    <textarea
      ref={ref}
      className={styles.ruledField}
      rows={rows}
      onChange={handleChange}
      {...props}
    />
  );
}
