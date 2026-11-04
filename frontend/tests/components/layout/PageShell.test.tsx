import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../../src/hooks/useAuth';
import { PageShell } from '../../../src/components/layout/PageShell';

vi.mock('../../../src/api/auth', () => ({
  logout: vi.fn().mockResolvedValue(undefined),
}));

const mockAuthValue = {
  token: 'test-token',
  userId: 'user-1',
  setAuth: vi.fn(),
  clearAuth: vi.fn(),
};

function renderShell(pageType: 'daily' | 'weekly' | 'monthly', path: string) {
  return render(
    <AuthContext.Provider value={mockAuthValue}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route
            path="*"
            element={
              <PageShell pageType={pageType}>
                <div>Content</div>
              </PageShell>
            }
          />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('PageShell', () => {
  it('renders Daily, Weekly, Monthly tabs', () => {
    renderShell('daily', '/daily/2026-11-03');
    expect(screen.getByText('Daily')).toBeInTheDocument();
    expect(screen.getByText('Weekly')).toBeInTheDocument();
    expect(screen.getByText('Monthly')).toBeInTheDocument();
  });

  it('marks the active tab correctly', () => {
    renderShell('weekly', '/weekly/2026/45');
    const weekly = screen.getByText('Weekly');
    expect(weekly.className).toMatch(/active/);
  });

  it('renders prev/next navigation buttons', () => {
    renderShell('daily', '/daily/2026-11-03');
    expect(screen.getByLabelText('Previous')).toBeInTheDocument();
    expect(screen.getByLabelText('Next')).toBeInTheDocument();
  });

  it('renders children', () => {
    renderShell('daily', '/daily/2026-11-03');
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders a log out button', () => {
    renderShell('daily', '/daily/2026-11-03');
    expect(screen.getByText('Log out')).toBeInTheDocument();
  });

  it('calls logout on log out click', async () => {
    const { logout } = await import('../../../src/api/auth');
    renderShell('daily', '/daily/2026-11-03');
    await userEvent.click(screen.getByText('Log out'));
    expect(logout).toHaveBeenCalled();
  });
});
