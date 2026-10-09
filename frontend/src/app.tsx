// Route table (REQ-FE-010/011).
//
// Nested layout: /login and /register sit under PublicOnlyRoute, the
// protected `/` tree sits under ProtectedRoute (t4's AppShell stays the
// shell it mounts into — not rewritten here).
//
// t22 ADDS the dashboard wiring only: "/" nests an index route rendering
// DashboardPage inside the AppShell outlet (the landing placeholder is
// replaced deliberately — app_shell.test.tsx is NOT edited).

import { Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/app_shell';
import { ProtectedRoute } from './components/common/protected_route';
import { PublicOnlyRoute } from './components/common/public_only_route';
import { LoginPage } from './pages/login_page';
import { RegisterPage } from './pages/register_page';
import { ExpensesPage } from './pages/expenses_page';
import { BudgetPage } from './pages/budget_page';
import { CategoriesPage } from './pages/categories_page';
import { DashboardPage } from './pages/dashboard_page';

export const App = (): JSX.Element => (
  <Routes>
    <Route element={<PublicOnlyRoute />}>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
    </Route>
    <Route element={<ProtectedRoute />}>
      <Route path="/" element={<AppShell />}>
        <Route index element={<DashboardPage />} />
      </Route>
      <Route path="/expenses" element={<ExpensesPage />} />
      <Route path="/budgets" element={<BudgetPage />} />
      <Route path="/categories" element={<CategoriesPage />} />
    </Route>
  </Routes>
);
