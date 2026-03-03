'use client';

import { useQuery } from '@tanstack/react-query';

export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
}

async function fetchUser(): Promise<User | null> {
  const res = await fetch('/api/auth/me', { credentials: 'include' });
  if (!res.ok) return null;
  return res.json();
}

export function useUser() {
  const {
    data: user = null,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['user'],
    queryFn: fetchUser,
    retry: false,
    staleTime: 30 * 1000,
  });

  return { user, isLoading, error, refetch };
}
