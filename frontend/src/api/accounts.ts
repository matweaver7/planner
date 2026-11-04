import { client } from './client';

export interface UserResponse {
  user_id: string;
  username: string;
  email: string;
  created_at: string;
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<UserResponse> {
  const response = await client.post<UserResponse>('/api/accounts/register', {
    username,
    email,
    password,
  });
  return response.data;
}
