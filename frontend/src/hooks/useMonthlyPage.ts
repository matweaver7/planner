import { useEffect, useState, useCallback } from 'react';
import { getMonthly, updateMonthly } from '../api/planner';
import type { MonthlyPage } from '../api/planner';

export function useMonthlyPage(year: number, month: number) {
  const [page, setPage] = useState<MonthlyPage | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setPage(null);
    getMonthly(year, month).then(setPage).catch(console.error);
  }, [year, month]);

  const save = useCallback(
    async (patch: Partial<MonthlyPage>) => {
      setSaving(true);
      try {
        const updated = await updateMonthly(year, month, patch);
        setPage(updated);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } catch (err) {
        console.error('Save failed', err);
      } finally {
        setSaving(false);
      }
    },
    [year, month],
  );

  const update = useCallback((patch: Partial<MonthlyPage>) => {
    setPage((prev) => (prev ? { ...prev, ...patch } : prev));
  }, []);

  return { page, saving, saved, save, update };
}
