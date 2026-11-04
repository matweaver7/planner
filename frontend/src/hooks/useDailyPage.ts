import { useEffect, useState, useCallback, useRef } from 'react';
import { getDaily, updateDaily } from '../api/planner';
import type { DailyPage } from '../api/planner';

const DEBOUNCE_MS = 500;

export function useDailyPage(date: string) {
  const [page, setPage] = useState<DailyPage | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setPage(null);
    getDaily(date).then(setPage).catch(console.error);
  }, [date]);

  const save = useCallback(
    async (patch: Partial<DailyPage>) => {
      setSaving(true);
      try {
        const updated = await updateDaily(date, patch);
        setPage(updated);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch (err) {
        console.error('Save failed', err);
      } finally {
        setSaving(false);
      }
    },
    [date],
  );

  const debouncedSave = useCallback(
    (patch: Partial<DailyPage>) => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => save(patch), DEBOUNCE_MS);
    },
    [save],
  );

  const update = useCallback((patch: Partial<DailyPage>) => {
    setPage((prev) => (prev ? { ...prev, ...patch } : prev));
  }, []);

  return { page, saving, saved, save, debouncedSave, update };
}
