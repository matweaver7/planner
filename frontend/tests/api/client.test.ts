import { describe, it, expect, beforeEach } from 'vitest';
import { setToken, getToken } from '../../src/api/client';

describe('client token management', () => {
  beforeEach(() => {
    setToken(null);
  });

  it('getToken returns null initially', () => {
    expect(getToken()).toBeNull();
  });

  it('setToken stores the token', () => {
    setToken('my-token');
    expect(getToken()).toBe('my-token');
  });

  it('setToken(null) clears the token', () => {
    setToken('my-token');
    setToken(null);
    expect(getToken()).toBeNull();
  });
});
