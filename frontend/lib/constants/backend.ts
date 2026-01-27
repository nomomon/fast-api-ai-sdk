/**
 * Backend API URL for client-side calls.
 * Falls back to http://localhost:8000 if NEXT_PUBLIC_BACKEND_URL is not set.
 */
export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
