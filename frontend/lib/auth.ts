import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

interface DecodedToken {
  sub: string;
  exp: number;
}

async function authenticateUser(payload: { email: string; password: string }) {
  try {
    const url = `${process.env.BASE_BACKEND_URL}/api/auth/token`;

    const res = await axios.post(url, payload);
    const data = await res.data;

    if (res.status === 200 && data.access_token) {
      const { sub } = jwtDecode<DecodedToken>(data.access_token);
      return {
        id: sub,
        email: payload.email,
      };
    }
    return null;
  } catch (error) {
    console.error('Login error:', error);
    return null;
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }
        return authenticateUser(credentials);
      },
    }),
  ],
  callbacks: {},

  pages: {
    signIn: '/login',
  },
};
