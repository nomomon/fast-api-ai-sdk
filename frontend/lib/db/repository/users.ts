/**
 * User repository functions for interacting with the FastAPI backend.
 *
 * Client-side calls use relative URLs that go through Next.js API proxy.
 * Server-side calls use the backend URL directly.
 */

// For server-side calls (NextAuth callbacks, server components)
const getServerBackendUrl = () => {
  return process.env.BASE_BACKEND_URL || 'http://localhost:8000';
};

// For client-side calls, use relative URLs that go through Next.js proxy
const getClientBackendUrl = () => {
  // Use relative URL to go through Next.js API proxy route
  return '';
};

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
 * This is called server-side from NextAuth, so it uses the backend URL directly.
 */
export async function verifyCredentials(data: LoginData): Promise<User | null> {
  try {
    const backendUrl = getServerBackendUrl();
    const response = await fetch(`${backendUrl}/api/auth/login`, {
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
 * This is called server-side from NextAuth, so it uses the backend URL directly.
 */
export async function userExistsByEmail(email: string): Promise<boolean> {
  try {
    const backendUrl = getServerBackendUrl();
    const response = await fetch(
      `${backendUrl}/api/auth/user-exists/${encodeURIComponent(email)}`,
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
    const backendUrl = getServerBackendUrl();
    const response = await fetch(`${backendUrl}/api/auth/me`, {
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
 * This is called from client-side, so it uses the Next.js API proxy route.
 */
export async function addUser(data: SignupData): Promise<User> {
  // Use relative URL to go through Next.js API proxy
  const backendUrl = getClientBackendUrl();
  const response = await fetch(`${backendUrl}/api/auth/signup`, {
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
