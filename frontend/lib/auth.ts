import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import type { NextAuthOptions, User } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

interface DecodedToken {
  sub: string;
  name: string;
  email: string;
  exp: number;
  iat: number;
}

async function authenticateUser(payload: {
  email: string;
  password: string;
}): Promise<User | null> {
  try {
    // Use Next.js API proxy - construct absolute URL for server-side request
    const baseUrl = process.env.BASE_BACKEND_URL;
    const url = `${baseUrl}/api/auth/token`;

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

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
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
        const userData = await authenticateUser(credentials);
        if (!userData) {
          return null;
        }
        // Return user object with accessToken in account
        return {
          id: userData.id,
          name: userData.name,
          email: userData.email,
          accessToken: userData.accessToken,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      // Initial sign in - store the access token and user data
      if (user && account) {
        token.accessToken = user.accessToken;
        token.id = user.id;
        token.name = user.name;
        token.email = user.email;
      }
      return token;
    },
    async session({ session, token }) {
      // Send properties to the client
      if (token && session.user) {
        session.user.id = token.id ?? '';
        session.user.name = token.name ?? '';
        session.user.email = token.email ?? '';
        session.accessToken = token.accessToken;
      }
      return session;
    },
  },

  pages: {
    signIn: '/login',
  },
};
