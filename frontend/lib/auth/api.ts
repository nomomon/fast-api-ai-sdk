import { cookies } from 'next/headers';
import { AUTH_COOKIE_MAX_AGE, AUTH_COOKIE_NAME } from './constants';

export function getBackendUrl(): string {
  return process.env.BASE_BACKEND_URL || 'http://localhost:8000';
}

export type FetchBackendResult =
  | { ok: true; status: number; data: unknown }
  | { ok: false; status: number; error: string };

/**
 * Fetch data from the backend on Next.js server components.
 * @param url - The URL to fetch.
 * @param options - The options to fetch with.
 * @returns The result of the fetch.
 */
export async function fetchBackend(
  path: string,
  options: { method: string; body?: object; token?: string }
): Promise<FetchBackendResult> {
  const url = `${getBackendUrl()}${path}`;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (options.token) headers.Authorization = `Bearer ${options.token}`;

  const res = await fetch(url, {
    method: options.method,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  const error = (data.detail ?? data.error ?? 'Request failed') as string;

  if (!res.ok) return { ok: false, status: res.status, error };
  return { ok: true, status: res.status, data };
}

export async function getAuthToken(): Promise<string | null> {
  const store = await cookies();
  return store.get(AUTH_COOKIE_NAME)?.value ?? null;
}

export async function setAuthCookie(token: string): Promise<void> {
  const store = await cookies();
  store.set(AUTH_COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/',
    maxAge: AUTH_COOKIE_MAX_AGE,
  });
}

export async function clearAuthCookie(): Promise<void> {
  const store = await cookies();
  store.delete(AUTH_COOKIE_NAME);
}
