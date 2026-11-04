import { useEffect, useState, useCallback } from 'react';
import { getWeekly, updateWeekly } from '../api/planner';
import type { WeeklyPage } from '../api/planner';

export function useWeeklyPage(year: number, week: number) {
  const [page, setPage] = useState<WeeklyPage | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setPage(null);
    getWeekly(year, week).then(setPage).catch(console.error);
  }, [year, week]);

  const save = useCallback(
    async (patch: Partial<WeeklyPage>) => {
      setSaving(true);
      try {
        const updated = await updateWeekly(year, week, patch);
        setPage(updated);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch (err) {
        console.error('Save failed', err);
      } finally {
        setSaving(false);
      }
    },
    [year, week],
  );

  const update = useCallback((patch: Partial<WeeklyPage>) => {
    setPage((prev) => (prev ? { ...prev, ...patch } : prev));
  }, []);

  return { page, saving, saved, save, update };
}
