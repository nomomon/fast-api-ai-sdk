/**
 * Client-side authenticated fetch wrapper. Uses credentials: 'include' so the
 * auth_token cookie is sent automatically; the API proxy reads it and adds
 * Bearer token to backend requests.
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
