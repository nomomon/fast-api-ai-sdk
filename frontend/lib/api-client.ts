/**
 * Authenticated fetch wrapper. Uses credentials: 'include' so the auth_token
 * cookie is sent automatically; the API proxy reads it and adds Bearer token.
 *
 * @param url - The URL to fetch (typically /api/*)
 * @param options - Fetch options (headers, body, etc.)
 * @returns Promise<Response>
 */
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const headers = new Headers(options.headers);

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  return fetch(url, {
    ...options,
    headers,
    credentials: 'include',
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
