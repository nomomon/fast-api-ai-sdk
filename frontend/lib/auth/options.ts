import type { NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import { signIn } from './signin';

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
        const userData = await signIn(credentials);
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
