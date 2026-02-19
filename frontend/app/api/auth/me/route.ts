import { NextResponse } from 'next/server';
import { fetchBackend, getAuthToken } from '@/lib/auth/api';

export async function GET() {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const result = await fetchBackend('/api/auth/me', { method: 'GET', token });
  if (!result.ok) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json(result.data);
}
