import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

interface DecodedToken {
  sub: string;
  id: string;
  role: string;
  exp: number;
}

async function auth(payload: { email: string; password: string }) {
  try {
    const url = `${process.env.BASE_BACKEND_URL}/api/auth/token`;
    console.log('Auth URL:', url);
    console.log('Auth Payload:', payload);

    const res = await axios.post(url, payload);

    const data = await res.data;
    const accessToken = data.access_token;

    if (res.status === 200 && accessToken) {
      // We return the token and username to be used in the JWT callback
      const { id, sub } = jwtDecode<DecodedToken>(accessToken);
      return {
        id,
        email: sub,
        accessToken,
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
        return auth(credentials);
      },
    }),
  ],
  callbacks: {
    // TODO: idk what this is doing, gonna fix a bit later
    async jwt({ token, user }) {
      // "user" is only available on the first time the JWT is created (on login)
      if (user) {
        token.accessToken = user.accessToken;
        token.email = user.email;
      }
      return token;
    },
    async session({ session, token }) {
      // Pass the token from the JWT to the client-side session
      session.user.role = token.role;
      session.accessToken = token.accessToken;
      session.user.email = token.email;
      return session;
    },
  },

  pages: {
    signIn: '/login',
  },
};
