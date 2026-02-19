import { NextResponse } from 'next/server';
import { fetchBackend, setAuthCookie } from '@/lib/auth/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = body;

    if (!email || !password) {
      return NextResponse.json({ error: 'Email and password are required' }, { status: 400 });
    }

    const result = await fetchBackend('/api/auth/token', {
      method: 'POST',
      body: { email, password },
    });

    if (!result.ok) {
      return NextResponse.json(
        { error: result.error || 'Invalid credentials' },
        { status: result.status }
      );
    }

    const token = (result.data as { access_token?: string })?.access_token;
    if (!token) {
      return NextResponse.json({ error: 'No token in response' }, { status: 500 });
    }

    await setAuthCookie(token);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json({ error: 'An unexpected error occurred' }, { status: 500 });
  }
}
