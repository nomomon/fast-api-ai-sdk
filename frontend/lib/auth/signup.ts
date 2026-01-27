'use server';

import axios, { AxiosError } from 'axios';

interface SignUpPayload {
  name: string;
  email: string;
  password: string;
}

interface SignUpResponse {
  success: boolean;
  error?: string;
}

export async function signUp(payload: SignUpPayload): Promise<SignUpResponse> {
  try {
    const baseUrl = process.env.BASE_BACKEND_URL;
    const url = `${baseUrl}/api/auth/signup`;

    const res = await axios.post(url, payload);
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
