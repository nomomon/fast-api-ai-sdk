'use client';

import { useRouter } from 'next/navigation';
import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Field, FieldDescription, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

async function signUp(_formData: FormData) {
  // TODO: Implement sign up logic to call backend API
  return {
    success: false,
    error: 'Sign up not implemented yet',
  };
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
    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('password', password);

    const result = await signUp(formData);

    if (result.success) {
      // Automatically sign in after sign up
      const signInResult = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });
      if (signInResult?.ok) {
        router.push('/');
      } else {
        router.push('/login');
      }
    } else {
      setError(result.error || 'Something went wrong');
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
