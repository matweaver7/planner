import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthContext } from '../../src/hooks/useAuth';
import { LoginPage } from '../../src/pages/LoginPage';

vi.mock('../../src/api/auth', () => ({
  login: vi.fn(),
  logout: vi.fn(),
}));

import { login } from '../../src/api/auth';

const mockToken =
  'eyJhbGciOiJIUzI1NiJ9.' +
  btoa(JSON.stringify({ sub: 'user-1', exp: 9999999999 })) +
  '.signature';

const mockSetAuth = vi.fn();
const mockAuthValue = {
  token: null as string | null,
  userId: null as string | null,
  setAuth: mockSetAuth,
  clearAuth: vi.fn(),
};

function renderLogin(token: string | null = null) {
  return render(
    <AuthContext.Provider value={{ ...mockAuthValue, token }}>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/daily/:date" element={<div>Daily page</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.mocked(login).mockResolvedValue({ token: mockToken, expires_at: '' });
    mockSetAuth.mockClear();
  });

  it('renders username and password fields', () => {
    renderLogin();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('renders a sign in button', () => {
    renderLogin();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('calls login with credentials on submit', async () => {
    renderLogin();
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'secret123');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => {
      expect(login).toHaveBeenCalledWith('alice', 'secret123');
    });
  });

  it('shows an error on failed login', async () => {
    vi.mocked(login).mockRejectedValue(new Error('401'));
    renderLogin();
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong');
    await userEvent.click(screen.getByRole('button', { name: /sign in/i }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  it('redirects to daily page if already authenticated', () => {
    renderLogin('existing-token');
    expect(screen.queryByLabelText('Username')).not.toBeInTheDocument();
    expect(screen.getByText('Daily page')).toBeInTheDocument();
  });

  it('has a link to the register page', () => {
    renderLogin();
    expect(screen.getByRole('link', { name: /create one/i })).toBeInTheDocument();
  });
});
