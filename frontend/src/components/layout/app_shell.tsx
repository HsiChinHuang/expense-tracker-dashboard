// AppShell — the authenticated application shell (REQ-FE-010/011, t4).
//
// t18 adds exactly two nav <Link>s (Budget / Categories) inside the
// existing <nav> — no layout rewrite; the three frozen AppShell nodes
// (header / tailwind container / main area) stay green and
// app_shell.test.tsx is NOT edited (Q2). Because the merged AppShell test
// renders the shell WITHOUT a Router, each link falls back to a plain
// anchor when no router context exists (useInRouterContext), so the same
// component renders real <Link>s in the app and inert anchors in the
// router-less unit test.
//
// t22 ADDS exactly two things: the Dashboard nav link (same guard-wrapped
// NavLink, now to "/") and the content outlet — useOutlet() renders the
// nested index route (DashboardPage) inside the routed app and is null in
// the router-less frozen test, where the ?? fallback keeps the original
// placeholder <p> byte-for-byte. app_shell.test.tsx is NOT edited.

import { Link, useInRouterContext, useOutlet } from 'react-router-dom';

interface NavLinkProps {
  to: string;
  children: string;
}

/** <Link> inside the app, plain <a> when rendered outside a Router. */
const NavLink = ({ to, children }: NavLinkProps): JSX.Element => {
  const inRouter = useInRouterContext();
  const className = 'text-slate-500 hover:text-slate-900';
  if (!inRouter) {
    return (
      <a className={className} href={to}>
        {children}
      </a>
    );
  }
  return (
    <Link className={className} to={to}>
      {children}
    </Link>
  );
};

export const AppShell = (): JSX.Element => {
  const outlet = useOutlet();
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="flex items-center justify-between p-4 bg-white shadow">
        <h1 className="text-xl font-semibold text-slate-900">Expense Tracker</h1>
        <nav className="flex gap-4">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/budgets">Budget</NavLink>
          <NavLink to="/categories">Categories</NavLink>
        </nav>
      </header>
      <main className="flex-1 p-4">
        {outlet ?? <p className="text-slate-600">Frontend skeleton is running.</p>}
      </main>
    </div>
  );
};
