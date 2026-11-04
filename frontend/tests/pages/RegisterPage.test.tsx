import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { RegisterPage } from '../../src/pages/RegisterPage';

vi.mock('../../src/api/accounts', () => ({
  register: vi.fn(),
}));

import { register } from '../../src/api/accounts';

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={['/register']}>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<div>Login page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(register).mockResolvedValue({
      user_id: 'u1',
      username: 'alice',
      email: 'a@example.com',
      created_at: '',
    });
  });

  it('renders all form fields', () => {
    renderRegister();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('calls register with correct values', async () => {
    renderRegister();
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Email'), 'alice@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'secret123');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => {
      expect(register).toHaveBeenCalledWith('alice', 'alice@example.com', 'secret123');
    });
  });

  it('shows an error for passwords shorter than 8 chars', async () => {
    renderRegister();
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Email'), 'alice@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'short');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(register).not.toHaveBeenCalled();
  });

  it('navigates to /login on success', async () => {
    renderRegister();
    await userEvent.type(screen.getByLabelText('Username'), 'alice');
    await userEvent.type(screen.getByLabelText('Email'), 'alice@example.com');
    await userEvent.type(screen.getByLabelText('Password'), 'secret123');
    await userEvent.click(screen.getByRole('button', { name: /create account/i }));
    await waitFor(() => {
      expect(screen.getByText('Login page')).toBeInTheDocument();
    });
  });
});
