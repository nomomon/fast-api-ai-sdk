'use client';

import axios, { AxiosError } from 'axios';
import { useRouter } from 'next/navigation';
import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Field, FieldDescription, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface SignUpResponse {
  success: boolean;
  error?: string;
}

async function signUp(data: {
  name: string;
  email: string;
  password: string;
}): Promise<SignUpResponse> {
  'use server';
  try {
    const url = `${process.env.BASE_BACKEND_URL}/api/auth/signup`;

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

export function SignUpForm({ className, ...props }: React.ComponentProps<'form'>) {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError('All fields are required');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    const result = await signUp({ name, email, password });

    if (result.success) {
      toast.success('Account created successfully!', {
        description: 'Signing you in...',
      });
      // Automatically sign in after sign up
      const signInResult = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });
      if (signInResult?.ok) {
        router.push('/');
      } else {
        toast.error('Account created but login failed', {
          description: 'Please try logging in manually.',
        });
        router.push('/login');
      }
    } else {
      const errorMessage = result.error || 'Something went wrong';
      setError(errorMessage);
      toast.error('Signup failed', {
        description: errorMessage,
      });
    }
  };

  return (
    <form className={cn('flex flex-col gap-6', className)} onSubmit={handleSubmit} {...props}>
      <FieldGroup>
        <div className="flex flex-col items-center gap-1 text-center">
          <h1 className="text-2xl font-bold">Create an account</h1>
          <p className="text-muted-foreground text-sm text-balance">
            Enter your details below to create your account
          </p>
        </div>
        {error && <div className="text-red-500 text-sm text-center">{error}</div>}
        <Field>
          <FieldLabel htmlFor="name">Name</FieldLabel>
          <Input
            id="name"
            type="text"
            placeholder="John Doe"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="email">Email</FieldLabel>
          <Input
            id="email"
            type="email"
            placeholder="m@example.com"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </Field>
        <Field>
          <FieldLabel htmlFor="password">Password</FieldLabel>
          <Input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Field>
        <Field>
          <Button type="submit">Sign Up</Button>
        </Field>
        <Field>
          <FieldDescription className="text-center">
            Already have an account?{' '}
            <a href="/login" className="underline underline-offset-4">
              Login
            </a>
          </FieldDescription>
        </Field>
      </FieldGroup>
    </form>
  );
}
