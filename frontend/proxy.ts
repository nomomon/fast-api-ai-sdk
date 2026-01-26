import { NextResponse } from 'next/server';
import { withAuth } from 'next-auth/middleware';

export default withAuth(
  function middleware(_req) {
    // You can add additional middleware logic here if needed
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
);

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/auth (NextAuth routes and signup endpoint)
     * - login (login page)
     * - signup (signup page)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - manifest.json / manifest.webmanifest (PWA manifest)
     * - public files (images, etc.)
     */
    '/((?!api/auth|login|signup|_next/static|_next/image|favicon.ico|manifest\\.(json|webmanifest)|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
