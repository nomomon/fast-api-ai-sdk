import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

const COOKIE_NAME = 'auth_token';

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get(COOKIE_NAME)?.value;
  const hasAuth = !!token;

  // Auth pages (login, signup): redirect to / if already logged in
  if (pathname === '/login' || pathname === '/signup') {
    if (hasAuth) {
      return NextResponse.redirect(new URL('/', request.url));
    }
    return NextResponse.next();
  }

  // Protected routes - redirect to login if not authenticated
  if (!hasAuth) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/auth (auth API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - manifest.json / manifest.webmanifest (PWA manifest)
     * - public files (images, etc.)
     * Note: login and signup ARE matched so we can redirect logged-in users
     */
    '/((?!api/auth|_next/static|_next/image|favicon.ico|manifest.json|manifest.webmanifest|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
