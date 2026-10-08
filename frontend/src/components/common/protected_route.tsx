// ProtectedRoute — gate for authenticated-only routes (REQ-FE-012).
//
// While the auth state is still loading (stored token being validated) a
// full-page spinner is shown. Unauthenticated visits are redirected to
// /login with the attempted location preserved in router state so the
// login page can send the user back afterwards (REQ-FE-013).

import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';

export const ProtectedRoute = (): JSX.Element => {
  const { token, isLoading } = useAuth();
  const location = useLocation();

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

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
};
