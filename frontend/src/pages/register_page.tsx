// RegisterPage (REQ-FE-061).
//
// Email / username / password / confirm password, validated on blur with a
// Zod schema mirroring the backend rules (min-8 password, 3-50 no-space
// username). Submits through the auth context — a successful register
// auto-logs-in with the returned 201 token. Backend 409/422 bodies carry
// `{code, field}`; the message is mapped onto the named field.

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { useAuth } from '../context/auth_context';
import { toApiError } from '../api/client';
import { zodResolver } from '../utils/validation';

const registerSchema = z
  .object({
    email: z.string().email('Email is required'),
    username: z
      .string()
      .min(3, 'Username must be at least 3 characters')
      .max(50, 'Username must be at most 50 characters')
      .regex(/^\S+$/, 'Username must not contain whitespace'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirmPassword: z.string()
  })
  .refine((values) => values.password === values.confirmPassword, {
    path: ['confirmPassword'],
    message: 'Passwords do not match'
  });

type RegisterForm = z.infer<typeof registerSchema>;

export const RegisterPage = (): JSX.Element => {
  const { register: registerAccount } = useAuth();
  const navigate = useNavigate();
  const [rootError, setRootError] = useState<string | null>(null);

  const {
    register: bindField,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting }
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    mode: 'onBlur',
    defaultValues: { email: '', username: '', password: '', confirmPassword: '' }
  });

  const onSubmit = async (values: RegisterForm): Promise<void> => {
    setRootError(null);
    try {
      await registerAccount({
        email: values.email,
        username: values.username,
        password: values.password
      });
      navigate('/', { replace: true });
    } catch (error) {
      const apiError = toApiError(error);
      if (apiError.field) {
        setError(apiError.field as keyof RegisterForm, {
          type: 'server',
          message: apiError.message
        });
      } else {
        setRootError(apiError.message);
      }
    }
  };

  return (
    <div className="mx-auto mt-16 max-w-sm">
      <h1 className="mb-4 text-2xl font-semibold text-slate-900">Create an account</h1>
      {rootError ? (
        <p className="mb-4 rounded bg-red-50 p-2 text-sm text-red-700" role="alert">
          {rootError}
        </p>
      ) : null}
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="register-email">
            Email
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="register-email"
            type="email"
            {...bindField('email')}
          />
          {errors.email ? (
            <p className="mt-1 text-sm text-red-600" id="register-email-error">
              {errors.email.message}
            </p>
          ) : null}
        </div>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="register-username">
            Username
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="register-username"
            type="text"
            {...bindField('username')}
          />
          {errors.username ? (
            <p className="mt-1 text-sm text-red-600" id="register-username-error">
              {errors.username.message}
            </p>
          ) : null}
        </div>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="register-password">
            Password
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="register-password"
            type="password"
            {...bindField('password')}
          />
          {errors.password ? (
            <p className="mt-1 text-sm text-red-600" id="register-password-error">
              {errors.password.message}
            </p>
          ) : null}
        </div>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="register-confirm-password">
            Confirm password
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="register-confirm-password"
            type="password"
            {...bindField('confirmPassword')}
          />
          {errors.confirmPassword ? (
            <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
          ) : null}
        </div>
        <button
          className="w-full rounded bg-slate-800 p-2 text-white disabled:opacity-50"
          disabled={isSubmitting}
          type="submit"
        >
          Register
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        Already registered?{' '}
        <Link className="text-blue-700 underline" to="/login">
          Log in
        </Link>
      </p>
    </div>
  );
};
