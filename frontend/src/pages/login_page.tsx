// LoginPage (REQ-FE-060, REQ-FE-013).
//
// Email + password validated client-side with a Zod schema mirroring the
// backend rules, submitted through the auth context. A normalized backend
// error (e.g. 401 INVALID_CREDENTIALS) renders inline with role="alert";
// on success the user lands on the preserved `from` location or `/`.

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { z } from 'zod';
import { useAuth } from '../context/auth_context';
import { toApiError, type ApiError } from '../api/client';
import { zodResolver } from '../utils/validation';

const loginSchema = z.object({
  email: z.string().email('Enter a valid email'),
  password: z.string().min(1, 'Password is required')
});

type LoginForm = z.infer<typeof loginSchema>;

interface LocationState {
  from?: { pathname?: string };
}

export const LoginPage = (): JSX.Element => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [apiError, setApiError] = useState<ApiError | null>(null);

  const {
    register: bindField,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' }
  });

  const onSubmit = async (values: LoginForm): Promise<void> => {
    setApiError(null);
    try {
      await login(values);
      const from = (location.state as LocationState | null)?.from?.pathname;
      navigate(from ?? '/', { replace: true });
    } catch (error) {
      setApiError(toApiError(error));
    }
  };

  return (
    <div className="mx-auto mt-16 max-w-sm">
      <h1 className="mb-4 text-2xl font-semibold text-slate-900">Log in</h1>
      {apiError ? (
        <p className="mb-4 rounded bg-red-50 p-2 text-sm text-red-700" role="alert">
          {apiError.message}
        </p>
      ) : null}
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="login-email">
            Email
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="login-email"
            type="email"
            {...bindField('email')}
          />
          {errors.email ? (
            <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
          ) : null}
        </div>
        <div>
          <label className="block text-sm text-slate-700" htmlFor="login-password">
            Password
          </label>
          <input
            className="w-full rounded border border-slate-300 p-2"
            id="login-password"
            type="password"
            {...bindField('password')}
          />
          {errors.password ? (
            <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
          ) : null}
        </div>
        <button
          className="w-full rounded bg-slate-800 p-2 text-white disabled:opacity-50"
          disabled={isSubmitting}
          type="submit"
        >
          Log in
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-600">
        No account yet?{' '}
        <Link className="text-blue-700 underline" to="/register">
          Register
        </Link>
      </p>
    </div>
  );
};
