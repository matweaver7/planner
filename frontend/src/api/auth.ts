import { client, setToken } from './client';

export interface LoginResponse {
  token: string;
  expires_at: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await client.post<LoginResponse>('/api/auth/login', {
    username,
    password,
  });
  setToken(response.data.token);
  return response.data;
}

export async function logout(token: string): Promise<void> {
  await client.post('/api/auth/logout', { token });
  setToken(null);
}
