import { type NextRequest, NextResponse } from 'next/server';

/**
 * Signup endpoint that proxies to the FastAPI backend.
 * This route takes precedence over NextAuth's catch-all route.
 */

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  const backendUrl = process.env.BASE_BACKEND_URL || 'http://localhost:8000';
  const url = new URL('/api/auth/signup', backendUrl);

  // Prepare headers
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');

  // Forward cookies
  const cookieHeader = request.headers.get('cookie');
  if (cookieHeader) {
    headers.set('cookie', cookieHeader);
  }

  try {
    // Get request body
    const body = await request.text();

    // Make request to backend
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers,
      body,
    });

    const responseBody = await response.text();

    // Create response with forwarded headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (key.toLowerCase() !== 'content-encoding' && key.toLowerCase() !== 'transfer-encoding') {
        responseHeaders.set(key, value);
      }
    });

    // Forward set-cookie headers
    const setCookieHeaders = response.headers.getSetCookie();
    setCookieHeaders.forEach((cookie) => {
      responseHeaders.append('set-cookie', cookie);
    });

    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Signup proxy error:', error);
    return NextResponse.json({ error: 'Failed to proxy request to backend' }, { status: 502 });
  }
}
