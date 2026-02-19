import { NextResponse } from 'next/server';
import { fetchBackend } from '@/lib/auth/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, email, password } = body;

    if (!name || !email || !password) {
      return NextResponse.json(
        { error: 'Name, email, and password are required' },
        { status: 400 }
      );
    }

    const result = await fetchBackend('/api/auth/signup', {
      method: 'POST',
      body: { name, email, password },
    });

    if (!result.ok) {
      return NextResponse.json(
        { error: result.error || 'Signup failed' },
        { status: result.status }
      );
    }

    return NextResponse.json({ success: true }, { status: 201 });
  } catch (error) {
    console.error('Signup error:', error);
    return NextResponse.json({ error: 'An unexpected error occurred' }, { status: 500 });
  }
}
