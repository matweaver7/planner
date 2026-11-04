import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { App } from '../src/App';

vi.mock('../src/api/planner', () => ({
  getDaily: vi.fn().mockResolvedValue({
    user_id: 'u1',
    date: '2026-11-03',
    time_blocks: [],
    notes: '',
    study_topic: '',
    exercise_plan: '',
    goals_for_today: '',
    to_do_list: '',
  }),
  getWeekly: vi.fn(),
  getMonthly: vi.fn(),
  updateDaily: vi.fn(),
  updateWeekly: vi.fn(),
  updateMonthly: vi.fn(),
}));

vi.mock('../src/api/auth', () => ({
  login: vi.fn(),
  logout: vi.fn(),
}));

vi.mock('../src/api/accounts', () => ({
  register: vi.fn(),
}));

describe('App routing', () => {
  it('redirects / to /login when unauthenticated', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders login page at /login', () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
  });

  it('renders register page at /register', () => {
    render(
      <MemoryRouter initialEntries={['/register']}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });
});
