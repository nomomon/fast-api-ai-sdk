/**
 * User repository functions for interacting with the FastAPI backend.
 */

const BASE_BACKEND_URL =
  process.env.NEXT_PUBLIC_BASE_BACKEND_URL ||
  process.env.BASE_BACKEND_URL ||
  'http://localhost:8000';

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface SignupData {
  name: string;
  email: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

/**
 * Verify user credentials and get user data.
 */
export async function verifyCredentials(data: LoginData): Promise<User | null> {
  try {
    const response = await fetch(`${BASE_BACKEND_URL}/api/auth/login`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error verifying credentials:', error);
    return null;
  }
}

/**
 * Check if a user exists by email (public endpoint, used for OAuth flows).
 */
export async function userExistsByEmail(email: string): Promise<boolean> {
  try {
    const response = await fetch(
      `${BASE_BACKEND_URL}/api/auth/user-exists/${encodeURIComponent(email)}`,
      {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    return data.exists === true;
  } catch (error) {
    console.error('Error checking if user exists:', error);
    return false;
  }
}

/**
 * Get user by email from the backend.
 * Note: This requires authentication, so it's mainly used server-side after NextAuth session is established.
 */
export async function getUserByEmail(email: string): Promise<User | null> {
  try {
    // First check if user exists (public endpoint)
    const exists = await userExistsByEmail(email);
    if (!exists) {
      return null;
    }

    // Then get user details from /auth/me (requires auth)
    const response = await fetch(`${BASE_BACKEND_URL}/api/auth/me`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      return null;
    }

    const user = await response.json();
    // Verify the email matches
    if (user.email === email) {
      return user;
    }
    return null;
  } catch (error) {
    console.error('Error fetching user by email:', error);
    return null;
  }
}

/**
 * Create a new user via the signup endpoint.
 */
export async function addUser(data: SignupData): Promise<User> {
  const response = await fetch(`${BASE_BACKEND_URL}/api/auth/signup`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create user' }));
    throw new Error(error.detail || 'Failed to create user');
  }

  return await response.json();
}
