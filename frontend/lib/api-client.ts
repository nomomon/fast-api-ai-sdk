import { getSession } from 'next-auth/react';

/**
 * Authenticated fetch wrapper that automatically adds JWT token to requests.
 *
 * @param url - The URL to fetch
 * @param options - Fetch options (headers, body, etc.)
 * @returns Promise<Response>
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const session = await getSession();
  const token = session?.accessToken;

  // Merge headers
  const headers = new Headers(options.headers);

  // Add authorization header if token exists
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Add content-type if body is present and not already set
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  return fetch(url, {
    ...options,
    headers,
  });
}

/**
 * Server-side authenticated fetch for use in API routes and server components.
 *
 * @param url - The URL to fetch
 * @param token - JWT token to use for authentication
 * @param options - Fetch options
 * @returns Promise<Response>
 */
export async function serverAuthenticatedFetch(
  url: string,
  token: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = new Headers(options.headers);

  // Add authorization header
  headers.set('Authorization', `Bearer ${token}`);

  // Add content-type if body is present and not already set
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  return fetch(url, {
    ...options,
    headers,
  });
}
