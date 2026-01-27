import { type NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth/options';

/**
 * Catch-all API route that proxies requests to the backend.
 * Reads BASE_BACKEND_URL from environment variables at runtime.
 * Automatically adds JWT token from NextAuth session to requests.
 */

// Route segment config for streaming support
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'POST');
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PUT');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'DELETE');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path, 'PATCH');
}

async function proxyRequest(request: NextRequest, pathSegments: string[], method: string) {
  // Get backend URL from environment variable (set at runtime)
  const backendUrl = process.env.BASE_BACKEND_URL || 'http://localhost:8000';

  // Reconstruct the path
  const path = pathSegments.join('/');
  const url = new URL(`/api/${path}`, backendUrl);

  // Copy query parameters
  request.nextUrl.searchParams.forEach((value, key) => {
    url.searchParams.append(key, value);
  });

  // Get session and extract JWT token
  const session = await getServerSession(authOptions);
  const token = session?.accessToken;

  // Prepare headers to forward
  const headers = new Headers();

  // Forward relevant headers
  const headersToForward = ['content-type', 'accept', 'accept-language', 'user-agent'];

  headersToForward.forEach((headerName) => {
    const value = request.headers.get(headerName);
    if (value) {
      headers.set(headerName, value);
    }
  });

  // Add authorization header with JWT token if available
  // Only add if not already present (allows manual override if needed)
  const existingAuth = request.headers.get('authorization');
  if (token && !existingAuth) {
    headers.set('Authorization', `Bearer ${token}`);
  } else if (existingAuth) {
    // Forward existing authorization header if present
    headers.set('Authorization', existingAuth);
  }

  try {
    // Get request body if present
    let body: BodyInit | undefined;
    if (method !== 'GET' && method !== 'HEAD') {
      const contentType = request.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        body = await request.text();
      } else if (contentType?.includes('text/')) {
        body = await request.text();
      } else {
        body = await request.arrayBuffer();
      }
    }

    // Make request to backend
    const response = await fetch(url.toString(), {
      method,
      headers,
      body,
    });

    // Handle 401 Unauthorized - token may be invalid or expired
    if (response.status === 401) {
      return NextResponse.json(
        { error: 'Unauthorized', detail: 'Invalid or expired token' },
        { status: 401 }
      );
    }

    // Check if this is a streaming response (for chat endpoint)
    const contentType = response.headers.get('content-type');
    const isStreaming = contentType?.includes('text/event-stream');

    if (isStreaming) {
      // For streaming responses, create a readable stream
      const stream = new ReadableStream({
        async start(controller) {
          const reader = response.body?.getReader();
          if (!reader) {
            controller.close();
            return;
          }

          try {
            while (true) {
              const { done, value } = await reader.read();
              if (done) {
                controller.close();
                break;
              }
              controller.enqueue(value);
            }
          } catch (error) {
            controller.error(error);
          }
        },
      });

      // Return streaming response with appropriate headers
      return new NextResponse(stream, {
        status: response.status,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          Connection: 'keep-alive',
        },
      });
    }

    // For non-streaming responses, get the body and forward it
    const responseBody = await response.text();

    // Create response with forwarded headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      // Forward relevant headers
      if (key.toLowerCase() !== 'content-encoding' && key.toLowerCase() !== 'transfer-encoding') {
        responseHeaders.set(key, value);
      }
    });

    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json({ error: 'Failed to proxy request to backend' }, { status: 502 });
  }
}
