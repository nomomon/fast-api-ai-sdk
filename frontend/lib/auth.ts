import { randomUUID } from 'crypto';
import { getServerSession, type NextAuthOptions } from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GithubProvider from 'next-auth/providers/github';
import { addUser, getUserByEmail, verifyCredentials } from '@/lib/db/repository/users';

export const authOptions: NextAuthOptions = {
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_ID as string,
      clientSecret: process.env.GITHUB_SECRET as string,
    }),
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

        const user = await verifyCredentials({
          email: credentials.email,
          password: credentials.password,
        });

        if (!user) {
          return null;
        }

        return {
          id: user.id.toString(),
          name: user.name,
          email: user.email,
        };
      },
    }),
  ],
  pages: {
    signIn: '/login',
  },
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider !== 'github') {
        return true;
      }

      const email = user.email || (profile as { email?: string } | null)?.email;
      if (!email) {
        return false;
      }

      // Check if user exists using public endpoint
      const { userExistsByEmail } = await import('@/lib/db/repository/users');
      const exists = await userExistsByEmail(email);

      if (exists) {
        return true;
      }

      // Generate a random password for GitHub users (they won't use it)
      const placeholderPassword = randomUUID();

      try {
        await addUser({
          name: user.name || (profile as { name?: string } | null)?.name || 'GitHub User',
          email,
          password: placeholderPassword,
        });
      } catch (error) {
        // Ignore unique constraint races; sign-in can still continue if another request just created the row.
        console.error('GitHub sign-in user create error', error);
      }

      return true;
    },
  },
};

export async function getAuthenticatedUser() {
  const session = await getServerSession(authOptions);
  if (!session?.user?.email) {
    return null;
  }

  const user = await getUserByEmail(session.user.email);
  return user || null;
}
