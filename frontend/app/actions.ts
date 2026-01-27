'use server';

import axios, { AxiosError } from 'axios';

interface SignUpResponse {
  success: boolean;
  error?: string;
}

export async function signUp(data: {
  name: string;
  email: string;
  password: string;
}): Promise<SignUpResponse> {
  try {
    // Use Next.js API proxy - construct absolute URL for server-side request
    const baseUrl = process.env.NEXTAUTH_URL || 'http://localhost:3000';
    const url = `${baseUrl}/api/auth/signup`;

    const res = await axios.post(url, data);
    const result = await res.data;

    return {
      success: result.success || true,
    };
  } catch (error: unknown) {
    console.error('Signup error:', error);
    if (!(error instanceof AxiosError)) {
      return {
        success: false,
        error: 'An unexpected error occurred. Please try again.',
      };
    }

    const errorMessage =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      'Network error. Please try again.';
    return {
      success: false,
      error: errorMessage,
    };
  }
}
