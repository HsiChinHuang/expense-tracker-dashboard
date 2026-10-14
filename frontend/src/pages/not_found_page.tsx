// NotFoundPage — the catch-all 404 route (REQ-FE-010/011, t60).
//
// Rendered by the `<Route path="*" element={<NotFoundPage />} />` in
// app.tsx, which sits as a SIBLING of the ProtectedRoute block on purpose:
// an unknown path must show this page rather than be bounced to /login by
// the auth guard. It therefore renders without the AppShell (no shell
// markup is asserted here) and offers a single way back: a link to the
// root route labelled "Back to Dashboard".
//
// The document title is exactly "Not Found" (the t60 card pins the copy),
// and the link is a plain react-router-dom <Link> to "/" — this page only
// ever renders inside a router, so no guard-wrap is needed.

import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export const NotFoundPage = (): JSX.Element => {
  useEffect(() => {
    document.title = 'Not Found';
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-slate-50 p-4">
      <h1 className="text-2xl font-semibold text-slate-900">Not Found</h1>
      <p className="text-slate-600">
        The page you are looking for does not exist.
      </p>
      <p>
        <Link
          className="rounded bg-slate-800 px-3 py-1 text-white"
          to="/"
        >
          Back to Dashboard
        </Link>
      </p>
    </div>
  );
};
