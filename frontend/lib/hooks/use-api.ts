import { useSession } from 'next-auth/react';
import { useCallback } from 'react';
import { authenticatedFetch } from '@/lib/api-client';

/**
 * Custom hook for making authenticated API calls.
 * Automatically includes JWT token from session.
 *
 * @returns Object with authenticated fetch function
 */
export function useApi() {
  const { data: session, status } = useSession();

  const fetch = useCallback(async (url: string, options: RequestInit = {}): Promise<Response> => {
    return authenticatedFetch(url, options);
  }, []);

  return {
    fetch,
    isAuthenticated: status === 'authenticated',
    isLoading: status === 'loading',
    session,
  };
}
