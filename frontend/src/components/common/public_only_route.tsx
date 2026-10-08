// PublicOnlyRoute — keeps logged-in users off /login and /register
// (REQ-FE-014): authenticated visitors are redirected to the landing
// route instead of seeing the auth forms again.

import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';

export const PublicOnlyRoute = (): JSX.Element => {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center" role="status">
        <span
          className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-700"
        />
        <span className="sr-only">Loading</span>
      </div>
    );
  }

  if (token) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};
