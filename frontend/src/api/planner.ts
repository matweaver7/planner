import { client } from './client';

// ── Daily ──────────────────────────────────────────────────────────────────

export interface TimeBlock {
  time: string;
  text: string;
}

export interface DailyPage {
  user_id: string;
  date: string;
  time_blocks: TimeBlock[];
  notes: string;
  study_topic: string;
  exercise_plan: string;
  goals_for_today: string;
  to_do_list: string;
}

export async function getDaily(date: string): Promise<DailyPage> {
  const response = await client.get<DailyPage>(`/api/planner/daily/${date}`);
  return response.data;
}

export async function updateDaily(date: string, patch: Partial<DailyPage>): Promise<DailyPage> {
  const response = await client.put<DailyPage>(`/api/planner/daily/${date}`, patch);
  return response.data;
}

// ── Weekly ─────────────────────────────────────────────────────────────────

export interface DayGlance {
  day: string;
  date: string;
  text: string;
}

export interface WeeklyPage {
  user_id: string;
  year: number;
  week: number;
  week_of_date: string;
  study_topic: string;
  educational_goal: string;
  exercise_goal: string;
  career_goal: string;
  other_goals: string;
  week_at_a_glance: DayGlance[];
}

export async function getWeekly(year: number, week: number): Promise<WeeklyPage> {
  const response = await client.get<WeeklyPage>(`/api/planner/weekly/${year}/${week}`);
  return response.data;
}

export async function updateWeekly(
  year: number,
  week: number,
  patch: Partial<WeeklyPage>,
): Promise<WeeklyPage> {
  const response = await client.put<WeeklyPage>(`/api/planner/weekly/${year}/${week}`, patch);
  return response.data;
}

// ── Monthly ────────────────────────────────────────────────────────────────

export interface MonthlyPage {
  user_id: string;
  year: number;
  month: number;
  study_topic: string;
  educational_goal: string;
  exercise_goal: string;
  career_goal: string;
  other_goals: string;
}

export async function getMonthly(year: number, month: number): Promise<MonthlyPage> {
  const response = await client.get<MonthlyPage>(`/api/planner/monthly/${year}/${month}`);
  return response.data;
}

export async function updateMonthly(
  year: number,
  month: number,
  patch: Partial<MonthlyPage>,
): Promise<MonthlyPage> {
  const response = await client.put<MonthlyPage>(`/api/planner/monthly/${year}/${month}`, patch);
  return response.data;
}
