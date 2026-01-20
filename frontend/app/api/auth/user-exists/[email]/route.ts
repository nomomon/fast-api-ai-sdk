import { type NextRequest, NextResponse } from 'next/server';

/**
 * Check if user exists endpoint that proxies to the FastAPI backend.
 * This route takes precedence over NextAuth's catch-all route.
 */

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ email: string }> }
) {
  const { email } = await params;
  const backendUrl = process.env.BASE_BACKEND_URL || 'http://localhost:8000';
  const url = new URL(`/api/auth/user-exists/${encodeURIComponent(email)}`, backendUrl);

  // Prepare headers
  const headers = new Headers();
  headers.set('Content-Type', 'application/json');

  // Forward cookies
  const cookieHeader = request.headers.get('cookie');
  if (cookieHeader) {
    headers.set('cookie', cookieHeader);
  }

  try {
    // Make request to backend
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers,
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
    console.error('User exists proxy error:', error);
    return NextResponse.json({ error: 'Failed to proxy request to backend' }, { status: 502 });
  }
}
