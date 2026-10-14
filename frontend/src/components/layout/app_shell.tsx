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
//
// t60 ADDS the fourth nav entry (Expenses → /expenses) through the SAME
// module-local guard-wrapped NavLink — no new hook, no raw react-router
// NavLink, and no auth state in the shell (logout stays t61 scope). The
// router-less frozen test still renders four inert anchors, so its three
// stored assertions stay green. app_shell.test.tsx is NOT edited.
//
// t61 IS that t61 scope, and supersedes the "no auth state in the shell"
// note above for this one control (operator ruling Q3a): the sign-out button
// now lives in the shell header so it works on every shell-wrapped page, and
// the in-page control is removed from the dashboard. The button is reached
// through two module-local components: <LogoutSlot /> reuses the SAME
// useInRouterContext fallback trick the nav links already use and renders
// NOTHING outside a Router, and <LogoutButton /> is the router-only leaf that
// reads the merged auth context and calls its untouched logout action. The
// gate is a component rather than an early return so no hook is ever called
// conditionally. Consequence, stated plainly: in the router-less frozen test
// the slot renders nothing and the three stored assertions never move; inside
// the app, where a provider always exists, the button renders. The
// post-logout redirect to /login stays the carried guard behaviour — no
// navigation hook, no location, no local state appears in this module.

import { Link, useInRouterContext, useOutlet } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';

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

/** The sign-out leaf: the merged logout action behind one button (t61). */
const LogoutButton = (): JSX.Element => {
  const { logout } = useAuth();
  return (
    <button
      type="button"
      onClick={logout}
      data-testid="logout-button"
      className="rounded border border-slate-300 px-2 py-1 text-sm text-slate-700"
    >
      Log out
    </button>
  );
};

/**
 * Renders <LogoutButton /> inside a Router, NOTHING outside one (t61).
 *
 * The frozen app_shell.test.tsx renders the shell with no Router and no auth
 * provider, so the fallback must be reached before the leaf is ever created —
 * the same shape the guard-wrapped anchors already use for inert <a>s.
 */
const LogoutSlot = (): JSX.Element | null => {
  const inRouter = useInRouterContext();
  if (!inRouter) {
    return null;
  }
  return <LogoutButton />;
};

export const AppShell = (): JSX.Element => {
  const outlet = useOutlet();
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <header className="flex items-center justify-between p-4 bg-white shadow">
        <h1 className="text-xl font-semibold text-slate-900">Expense Tracker</h1>
        <div className="flex items-center gap-4">
          <nav className="flex gap-4">
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/expenses">Expenses</NavLink>
            <NavLink to="/budgets">Budget</NavLink>
            <NavLink to="/categories">Categories</NavLink>
          </nav>
          <LogoutSlot />
        </div>
      </header>
      <main className="flex-1 p-4">
        {outlet ?? <p className="text-slate-600">Frontend skeleton is running.</p>}
      </main>
    </div>
  );
};
