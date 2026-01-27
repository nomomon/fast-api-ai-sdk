'use server';

import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import type { User } from 'next-auth';

interface SignInPayload {
  email: string;
  password: string;
}

interface DecodedToken {
  sub: string;
  name: string;
  email: string;
  exp: number;
  iat: number;
}

export async function signIn(payload: SignInPayload): Promise<User | null> {
  try {
    const url = `${process.env.BASE_BACKEND_URL}/api/auth/token`;

    const res = await axios.post(url, payload);
    const data = await res.data;

    if (res.status === 200 && data.access_token) {
      const decoded = jwtDecode<DecodedToken>(data.access_token);
      return {
        id: decoded.sub,
        name: decoded.name,
        email: decoded.email,
        accessToken: data.access_token,
      };
    }
    return null;
  } catch (error) {
    console.error('Login error:', error);
    return null;
  }
}
