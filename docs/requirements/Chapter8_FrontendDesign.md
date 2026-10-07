# Chapter 8: Frontend Design

## 8.1 Directory Structure and Layering

### 8.1.1 Full Frontend Tree

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── categories.ts
│   │   ├── expenses.ts
│   │   ├── budgets.ts
│   │   ├── dashboard.ts
│   │   └── health.ts
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── Badge.tsx
│   │   ├── layout/
│   │   │   ├── AppShell.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── MonthPicker.tsx
│   │   ├── charts/
│   │   │   ├── CategoryPieChart.tsx
│   │   │   ├── MonthlyTrendChart.tsx
│   │   │   ├── CumulativeLineChart.tsx
│   │   │   ├── WeeklyHeatmap.tsx
│   │   │   └── BudgetProgress.tsx
│   │   ├── forms/
│   │   │   ├── ExpenseForm.tsx
│   │   │   ├── BudgetForm.tsx
│   │   │   ├── CategoryForm.tsx
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   └── common/
│   │       ├── EmptyState.tsx
│   │       ├── ErrorState.tsx
│   │       ├── LoadingState.tsx
│   │       ├── ConfirmDialog.tsx
│   │       └── ProtectedRoute.tsx
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── ExpensesPage.tsx
│   │   ├── BudgetPage.tsx
│   │   ├── CategoriesPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useCategories.ts
│   │   ├── useExpenses.ts
│   │   ├── useBudgets.ts
│   │   ├── useDashboard.ts
│   │   └── useToast.ts
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   ├── MonthContext.tsx
│   │   └── ToastContext.tsx
│   ├── types/
│   │   ├── api.ts
│   │   └── domain.ts
│   ├── utils/
│   │   ├── format.ts
│   │   ├── date.ts
│   │   ├── validation.ts
│   │   └── color.ts
│   └── test/
│       ├── setup.ts
│       ├── mocks/
│       │   ├── handlers.ts
│       │   └── server.ts
│       └── fixtures/
├── public/
├── index.html
├── package.json
├── package-lock.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── .eslintrc.cjs
├── .prettierrc
└── Dockerfile
```

### 8.1.2 Layer Responsibilities

| Layer | Directory | Responsibility | Must Not |
|---|---|---|---|
| Entry | `main.tsx`, `App.tsx` | Bootstrap, providers, routes | Contain business logic |
| Pages | `pages/` | Compose components for a route | Call axios directly |
| Components | `components/` | Reusable UI, charts, forms | Know about routes |
| Hooks | `hooks/` | Data fetching and mutations | Render UI |
| Context | `context/` | Global client state | Fetch server data |
| API | `api/` | HTTP calls, request/response types | Contain React code |
| Utils | `utils/` | Pure functions | Import React |
| Types | `types/` | TypeScript definitions | Contain runtime code |

### 8.1.3 Import Direction

```
pages → components → hooks → api → client
  │         │         │
  │         │         └── context (read-only)
  │         └── utils
  └── context, hooks
```

Rules:
- Pages may import anything below them
- Components may not import pages
- Hooks may not import components or pages
- API modules may not import React
- Utils are pure and may not import React or API

## 8.2 Routing Design

### 8.2.1 Route Table

| Path | Page | Auth | Notes |
|---|---|---|---|
| `/login` | LoginPage | No | Redirect to `/` if already logged in |
| `/register` | RegisterPage | No | Redirect to `/` if already logged in |
| `/` | DashboardPage | Yes | Default landing after login |
| `/expenses` | ExpensesPage | Yes | List, filter, create, edit, delete |
| `/budgets` | BudgetPage | Yes | Set and view monthly budget |
| `/categories` | CategoriesPage | Yes | List and manage custom categories |
| `*` | NotFoundPage | - | 404 page |

### 8.2.2 Router Setup

```tsx
// App.tsx
import { Routes, Route, Navigate } from "react-router-dom";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/budgets" element={<BudgetPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
```

### 8.2.3 ProtectedRoute

```tsx
// components/common/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { FullPageSpinner } from "../ui/Spinner";

export function ProtectedRoute() {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <FullPageSpinner />;

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
```

### 8.2.4 Redirect After Login

```tsx
// LoginPage.tsx
const location = useLocation();
const navigate = useNavigate();
const from = location.state?.from?.pathname || "/";

// After successful login
navigate(from, { replace: true });
```

### 8.2.5 Public Route Guard

If a logged-in user visits `/login` or `/register`, redirect to `/`.

```tsx
function PublicOnlyRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  if (isLoading) return <FullPageSpinner />;
  if (user) return <Navigate to="/" replace />;
  return <>{children}</>;
}
```

### 8.2.6 Page Titles

Each page sets `document.title`:

| Route | Title |
|---|---|
| `/login` | Sign In — Expense Tracker |
| `/register` | Create Account — Expense Tracker |
| `/` | Dashboard — Expense Tracker |
| `/expenses` | Expenses — Expense Tracker |
| `/budgets` | Budget — Expense Tracker |
| `/categories` | Categories — Expense Tracker |
| `*` | Not Found — Expense Tracker |

## 8.3 Provider Nesting

### 8.3.1 Order

```tsx
// main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { App } from "./App";
import { AuthProvider } from "./context/AuthContext";
import { MonthProvider } from "./context/MonthContext";
import { ToastProvider } from "./context/ToastContext";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      gcTime: 10 * 60 * 1000,
      retry: (failureCount, error: any) => {
        if (error?.status === 401 || error?.status === 403) return false;
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: { retry: 0 },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <MonthProvider>
            <ToastProvider>
              <App />
            </ToastProvider>
          </MonthProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 8.3.2 Rationale

| Provider | Why This Position |
|---|---|
| QueryClientProvider | Outermost; AuthProvider calls useQuery |
| BrowserRouter | Needed by AuthProvider for redirects |
| AuthProvider | MonthProvider only meaningful when logged in |
| MonthProvider | Toast can be used anywhere including auth pages |
| ToastProvider | Innermost; any component can trigger a toast |

### 8.3.3 Provider Responsibilities

| Provider | Provides | Persists |
|---|---|---|
| QueryClientProvider | Server cache, retry, invalidation | In-memory |
| BrowserRouter | Route location, navigation | URL |
| AuthProvider | `user`, `token`, `login`, `logout`, `isLoading` | localStorage (token) |
| MonthProvider | `yearMonth`, `setYearMonth`, `prevMonth`, `nextMonth` | React state |
| ToastProvider | `showToast(message, variant)` | In-memory |

## 8.4 State Management

### 8.4.1 State Categories

| Category | Tool | Examples |
|---|---|---|
| Server state | TanStack Query | Expenses, budgets, dashboard data |
| Auth state | React Context | Logged-in user, token |
| UI state (global) | React Context | Selected month, toast queue |
| UI state (local) | `useState` | Modal open, form values |
| Form state | React Hook Form | Field values, errors, touched |
| URL state | React Router | Route params, query strings |

### 8.4.2 AuthContext

```tsx
// context/AuthContext.tsx
type AuthState = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem("token")
  );
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    authApi.me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      })
      .finally(() => setIsLoading(false));
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    localStorage.setItem("token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (email: string, username: string, password: string) => {
    await authApi.register({ email, username, password });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

### 8.4.3 MonthContext

```tsx
// context/MonthContext.tsx
type MonthState = {
  yearMonth: string;
  setYearMonth: (ym: string) => void;
  prevMonth: () => void;
  nextMonth: () => void;
};

export function MonthProvider({ children }: { children: React.ReactNode }) {
  const [yearMonth, setYearMonth] = useState(currentYearMonth());

  const prevMonth = () => setYearMonth((ym) => shiftMonth(ym, -1));
  const nextMonth = () => setYearMonth((ym) => shiftMonth(ym, 1));

  return (
    <MonthContext.Provider value={{ yearMonth, setYearMonth, prevMonth, nextMonth }}>
      {children}
    </MonthContext.Provider>
  );
}
```

### 8.4.4 ToastContext

```tsx
// context/ToastContext.tsx
type Toast = {
  id: string;
  message: string;
  variant: "success" | "error" | "info";
};

type ToastState = {
  showToast: (message: string, variant?: Toast["variant"]) => void;
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = (message: string, variant: Toast["variant"] = "info") => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, message, variant }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer toasts={toasts} />
    </ToastContext.Provider>
  );
}
```

### 8.4.5 Data Hooks

Each resource has a dedicated hook that wraps React Query.

```tsx
// hooks/useExpenses.ts
export function useExpenses(filters: ExpenseFilters) {
  return useQuery({
    queryKey: queryKeys.expenses.list(filters),
    queryFn: () => expensesApi.list(filters),
  });
}

export function useCreateExpense() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: expensesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["expenses"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
```

### 8.4.6 Hook List

| Hook | Query/Mutation | Invalidates |
|---|---|---|
| `useAuth` | Context | - |
| `useCategories` | Query | - |
| `useCreateCategory` | Mutation | categories |
| `useDeleteCategory` | Mutation | categories |
| `useExpenses` | Query | - |
| `useExpense` | Query | - |
| `useCreateExpense` | Mutation | expenses, dashboard |
| `useUpdateExpense` | Mutation | expenses, dashboard |
| `useDeleteExpense` | Mutation | expenses, dashboard |
| `useBudget` | Query | - |
| `useSetBudget` | Mutation | budgets, dashboard |
| `useDeleteBudget` | Mutation | budgets, dashboard |
| `useDashboardSummary` | Query | - |
| `useDashboardByCategory` | Query | - |
| `useDashboardTrend` | Query | - |
| `useDashboardCumulative` | Query | - |
| `useDashboardHeatmap` | Query | - |
| `useDashboardRecent` | Query | - |
| `useToast` | Context | - |

## 8.5 API Client

### 8.5.1 Axios Instance

```ts
// api/client.ts
import axios, { AxiosError } from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const client = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(normalizeError(error));
  }
);
```

### 8.5.2 Error Normalization

```ts
// api/client.ts
export type NormalizedError = {
  status: number;
  code: string;
  message: string;
  field?: string;
};

function normalizeError(error: AxiosError<ApiError>): NormalizedError {
  if (error.response) {
    const data = error.response.data;
    return {
      status: error.response.status,
      code: data?.code || "UNKNOWN_ERROR",
      message: data?.detail || "Something went wrong",
      field: data?.field,
    };
  }
  if (error.request) {
    return {
      status: 0,
      code: "NETWORK_ERROR",
      message: "Network error. Check your connection.",
    };
  }
  return {
    status: 0,
    code: "UNKNOWN_ERROR",
    message: error.message,
  };
}
```

### 8.5.3 Resource Modules

Each resource has its own module with typed functions.

```ts
// api/expenses.ts
import { client } from "./client";
import type {
  Expense,
  ExpenseListResponse,
  CreateExpenseInput,
  UpdateExpenseInput,
  ExpenseFilters,
} from "../types/api";

export const expensesApi = {
  list: async (filters: ExpenseFilters): Promise<ExpenseListResponse> => {
    const { data } = await client.get("/expenses", { params: filters });
    return data;
  },

  get: async (id: string): Promise<Expense> => {
    const { data } = await client.get(`/expenses/${id}`);
    return data;
  },

  create: async (input: CreateExpenseInput): Promise<Expense> => {
    const { data } = await client.post("/expenses", input);
    return data;
  },

  update: async (id: string, input: UpdateExpenseInput): Promise<Expense> => {
    const { data } = await client.put(`/expenses/${id}`, input);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await client.delete(`/expenses/${id}`);
  },
};
```

### 8.5.4 API Module List

| Module | Endpoints |
|---|---|
| `api/auth.ts` | register, login, me |
| `api/categories.ts` | list, create, delete |
| `api/expenses.ts` | list, get, create, update, delete |
| `api/budgets.ts` | get, set, delete |
| `api/dashboard.ts` | summary, byCategory, trend, cumulative, heatmap, recent |
| `api/health.ts` | health |

### 8.5.5 Why Centralized API Layer

| Benefit | Explanation |
|---|---|
| Single place for auth header | Interceptor attaches token |
| Single place for error handling | 401 redirect, error normalization |
| Easy to mock | MSW intercepts `client` calls |
| Type safety | Request and response types in one place |
| Backend contract alignment | Each function maps to one OpenAPI endpoint |

## 8.6 Query Key Specification

### 8.6.1 Query Key Factory

```ts
// api/queryKeys.ts
export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
  categories: {
    all: ["categories"] as const,
  },
  expenses: {
    all: ["expenses"] as const,
    list: (filters: ExpenseFilters) => ["expenses", "list", filters] as const,
    detail: (id: string) => ["expenses", "detail", id] as const,
  },
  budgets: {
    all: ["budgets"] as const,
    byMonth: (ym: string) => ["budgets", ym] as const,
  },
  dashboard: {
    all: ["dashboard"] as const,
    summary: (ym: string) => ["dashboard", "summary", ym] as const,
    byCategory: (ym: string) => ["dashboard", "by-category", ym] as const,
    trend: (months: number) => ["dashboard", "trend", months] as const,
    cumulative: (ym: string) => ["dashboard", "cumulative", ym] as const,
    heatmap: (weeks: number) => ["dashboard", "heatmap", weeks] as const,
    recent: (limit: number) => ["dashboard", "recent", limit] as const,
  },
};
```

### 8.6.2 Invalidation Strategy

| Mutation | Invalidates |
|---|---|
| Create expense | `["expenses"]`, `["dashboard"]` |
| Update expense | `["expenses"]`, `["dashboard"]` |
| Delete expense | `["expenses"]`, `["dashboard"]` |
| Set budget | `["budgets"]`, `["dashboard"]` |
| Delete budget | `["budgets"]`, `["dashboard"]` |
| Create category | `["categories"]` |
| Delete category | `["categories"]` |

Invalidating `["dashboard"]` invalidates all dashboard queries because
they share the same prefix.

### 8.6.3 Query Configuration

| Setting | Value | Rationale |
|---|---|---|
| `staleTime` | 5 minutes | Dashboard data does not change every second |
| `gcTime` | 10 minutes | Keep unused data for back navigation |
| `retry` | 3 for network, 0 for 4xx | Do not retry auth or validation errors |
| `refetchOnWindowFocus` | false | Avoid surprise refetches during review |
| `refetchOnMount` | true (default) | Fresh data when navigating back |

## 8.7 Page Design

### 8.7.1 LoginPage

**Layout**:

```
┌──────────────────────────────────────────────┐
│                                              │
│           ┌────────────────────┐             │
│           │   Expense Tracker  │             │
│           │   & Budget         │             │
│           │   Dashboard        │             │
│           │                    │             │
│           │  ┌──────────────┐  │             │
│           │  │ Email        │  │             │
│           │  └──────────────┘  │             │
│           │  ┌──────────────┐  │             │
│           │  │ Password     │  │             │
│           │  └──────────────┘  │             │
│           │                    │             │
│           │  [   Sign In    ]  │             │
│           │                    │             │
│           │  No account?       │             │
│           │  Create one        │             │
│           └────────────────────┘             │
│                                              │
└──────────────────────────────────────────────┘
```

**Behavior**:
- On mount, if already logged in, redirect to `/`
- Submit calls `useAuth().login(email, password)`
- On success, redirect to `from` or `/`
- On error, show inline error message
- "Create one" links to `/register`
- Form disables submit button while loading

### 8.7.2 RegisterPage

**Fields**:
- Email (required, valid email)
- Username (required, 3-50 chars, alphanumeric + underscore)
- Password (required, min 8 chars)
- Confirm password (must match)

**Behavior**:
- On success, auto-login and redirect to `/`
- Show field-level errors from backend
- Link to `/login` for existing users

### 8.7.3 DashboardPage

**Layout**:

```
┌──────────────────────────────────────────────────────────┐
│ Header: Logo | Month Picker | User Menu                  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Total   │ │ Budget  │ │ Usage   │ │ Trans-  │        │
│  │ Spent   │ │ Remaining│ │ Rate   │ │ actions │        │
│  │ $1250.50│ │ $749.50 │ │ 62.5%   │ │ 23      │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
│                                                           │
│  ┌──────────────────────┐ ┌──────────────────────────┐   │
│  │                      │ │                          │   │
│  │  Category Pie Chart  │ │  Monthly Trend Bar Chart │   │
│  │                      │ │                          │   │
│  └──────────────────────┘ └──────────────────────────┘   │
│                                                           │
│  ┌──────────────────────┐ ┌──────────────────────────┐   │
│  │                      │ │                          │   │
│  │  Cumulative Line     │ │  Weekly Heatmap          │   │
│  │  (with budget line)  │ │  (12 weeks)              │   │
│  │                      │ │                          │   │
│  └──────────────────────┘ └──────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Budget Progress Bar                                  │ │
│  │  ████████████░░░░░░░░  $1250.50 of $2000.00 (62.5%)  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Recent Transactions                                  │ │
│  │  ● Food & Dining    Oct 15    $45.00    Lunch        │ │
│  │  ● Groceries        Oct 14    $120.50   Weekly shop  │ │
│  │  ● Transportation   Oct 13    $25.00    Gas          │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Responsive**:
- Mobile: single column
- Tablet: KPI cards 2x2, charts stacked
- Desktop: KPI cards 4x1, charts 2x2

**Data Flow**:
- MonthContext provides `yearMonth`
- Six parallel queries triggered by `yearMonth`
- Each chart has independent loading state
- Changing month invalidates all dashboard queries

### 8.7.4 ExpensesPage

**Layout**:

```
┌──────────────────────────────────────────────────────────┐
│ Header                                                    │
├──────────────────────────────────────────────────────────┤
│ Filters: [Month ▾] [Category ▾]          [+ Add Expense] │
├──────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐ │
│ │ Date     │ Category        │ Amount  │ Note  │ Actions│ │
│ ├──────────────────────────────────────────────────────┤ │
│ │ Oct 15   │ ● Food & Dining │ $45.00  │ Lunch │ ✏ 🗑  │ │
│ │ Oct 14   │ ● Groceries     │ $120.50 │ ...   │ ✏ 🗑  │ │
│ │ Oct 13   │ ● Transportation│ $25.00  │ Gas   │ ✏ 🗑  │ │
│ └──────────────────────────────────────────────────────┘ │
│                                                           │
│ Pagination: [< Prev]  Page 1 of 3  [Next >]              │
└──────────────────────────────────────────────────────────┘
```

**Modal**: ExpenseForm opens on "Add Expense" or edit icon.

**Delete**: ConfirmDialog before deletion.

### 8.7.5 BudgetPage

**Layout**:

```
┌──────────────────────────────────────────────────────────┐
│ Header                                                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Month: [October 2026 ▾]                                  │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Current Budget                                       │ │
│  │  $2000.00                                             │ │
│  │  [Edit]  [Delete]                                     │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Set New Budget                                       │ │
│  │  Amount: [___________]  [Save]                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Budget History (last 12 months)                      │ │
│  │  Oct 2026    $2000.00                                 │ │
│  │  Sep 2026    $1800.00                                 │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 8.7.6 CategoriesPage

**Layout**:

```
┌──────────────────────────────────────────────────────────┐
│ Header                                                    │
├──────────────────────────────────────────────────────────┤
│                                        [+ Add Category]   │
├──────────────────────────────────────────────────────────┤
│  System Categories                                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ ● Food & Dining    #EF4444    (system)               │ │
│  │ ● Groceries        #F97316    (system)               │ │
│  │ ...                                                   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  My Categories                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ ● Side Project     #A855F7    [Delete]               │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

System categories have no delete button.

## 8.8 Chart Components

### 8.8.1 CategoryPieChart

**Props**:
```ts
type Props = {
  data: CategorySummary[];
  isLoading: boolean;
};
```

**Data transformation**:
```ts
function toPieData(categories: CategorySummary[]) {
  if (categories.length <= 6) return categories;

  const top6 = categories.slice(0, 6);
  const rest = categories.slice(6);
  const otherAmount = rest.reduce((s, c) => s + parseFloat(c.amount), 0);
  const otherPercent = rest.reduce((s, c) => s + c.percentage, 0);

  return [
    ...top6,
    {
      category_id: "other",
      name: "Other",
      color: "#6B7280",
      amount: otherAmount.toFixed(2),
      percentage: otherPercent,
    },
  ];
}
```

**Rendering**:
- Recharts `PieChart` + `Pie` + `Cell` + `Tooltip` + `Legend`
- Colors from `category.color`
- Tooltip shows name, amount, percentage
- Empty state: "No expenses this month"

### 8.8.2 MonthlyTrendChart

**Props**:
```ts
type Props = {
  data: { year_month: string; total: string }[];
  isLoading: boolean;
};
```

**Rendering**:
- Recharts `BarChart` + `Bar` + `XAxis` + `YAxis` + `Tooltip`
- X-axis labels formatted as "Oct 26"
- Y-axis formatted as USD
- Bar color: `#3B82F6`
- Empty state: "No data for this period"

### 8.8.3 CumulativeLineChart

**Props**:
```ts
type Props = {
  days: { date: string; daily: string; cumulative: string }[];
  budget: string;
  isLoading: boolean;
};
```

**Rendering**:
- Recharts `LineChart` + `Line` + `ReferenceLine`
- Line color: `#3B82F6` normally, `#EF4444` when over budget
- Budget line: `#9CA3AF` dashed
- X-axis: day of month
- Y-axis: USD
- Empty state: "No spending this month"

**Over-budget logic**:
```ts
const isOverBudget = days.some(
  (d) => parseFloat(d.cumulative) > parseFloat(budget)
);
```

### 8.8.4 WeeklyHeatmap

**Props**:
```ts
type Props = {
  weeks: { week_start: string; days: { date: string; amount: string }[] }[];
  maxAmount: string;
  isLoading: boolean;
};
```

**Rendering**:
- Custom grid: 12 columns (weeks) x 7 rows (days)
- Each cell colored by amount
- Tooltip: date + amount
- Legend: color gradient

**Color scale**:
```ts
function getColor(amount: number, max: number): string {
  if (amount === 0) return "#F3F4F6";
  const ratio = amount / max;
  if (ratio < 0.25) return "#DBEAFE";
  if (ratio < 0.5) return "#93C5FD";
  if (ratio < 0.75) return "#3B82F6";
  return "#1E40AF";
}
```

**Edge cases**:
- `max === 0`: all cells grey
- Missing days: treated as 0

### 8.8.5 BudgetProgress

**Props**:
```ts
type Props = {
  totalSpent: string;
  budget: string;
  percentage: number | null;
  isOverBudget: boolean;
};
```

**Rendering**:
- Progress bar: `width = min(percentage, 100)%`
- Color:
  - `< 80%`: green
  - `80-100%`: yellow
  - `> 100%`: red
- Text: `$1250.50 of $2000.00 (62.5%)`
- If `budget === 0`: "No budget set"

**State logic**:
```ts
function getState(spent: number, budget: number) {
  if (budget === 0) return { percentage: 0, color: "gray", label: "No budget set" };
  const pct = (spent / budget) * 100;
  if (pct > 100) return { percentage: 100, color: "red", label: "Over budget" };
  if (pct > 80) return { percentage: pct, color: "yellow", label: "Approaching limit" };
  return { percentage: pct, color: "green", label: "On track" };
}
```

## 8.9 Form Design

### 8.9.1 Validation Schemas

```ts
// utils/validation.ts
import { z } from "zod";

export const amountSchema = z
  .string()
  .regex(/^\d+(\.\d{1,2})?$/, "Invalid amount format")
  .refine((v) => parseFloat(v) > 0, "Amount must be positive")
  .refine((v) => parseFloat(v) <= 9999999999.99, "Amount too large");

export const expenseFormSchema = z.object({
  amount: amountSchema,
  category_id: z.string().uuid("Select a category"),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Invalid date"),
  note: z.string().max(500, "Note too long").optional(),
});

export const budgetFormSchema = z.object({
  amount: amountSchema,
});

export const categoryFormSchema = z.object({
  name: z.string().min(1).max(100),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, "Invalid color"),
});

export const loginFormSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Password required"),
});

export const registerFormSchema = z.object({
  email: z.string().email("Invalid email"),
  username: z.string()
    .min(3, "At least 3 characters")
    .max(50, "At most 50 characters")
    .regex(/^[a-zA-Z0-9_]+$/, "Letters, numbers, underscore only"),
  password: z.string().min(8, "At least 8 characters"),
});
```

### 8.9.2 ExpenseForm

```tsx
// components/forms/ExpenseForm.tsx
export function ExpenseForm({ initial, onSuccess, onCancel }: Props) {
  const { data: categories } = useCategories();
  const create = useCreateExpense();
  const update = useUpdateExpense();
  const { showToast } = useToast();

  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<ExpenseFormValues>({
      resolver: zodResolver(expenseFormSchema),
      defaultValues: initial || {
        amount: "",
        category_id: "",
        date: todayISO(),
        note: "",
      },
    });

  const onSubmit = async (values: ExpenseFormValues) => {
    try {
      if (initial) {
        await update.mutateAsync({ id: initial.id, ...values });
        showToast("Expense updated", "success");
      } else {
        await create.mutateAsync(values);
        showToast("Expense added", "success");
      }
      onSuccess();
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input label="Amount" {...register("amount")} error={errors.amount?.message} />
      <Select label="Category" {...register("category_id")} error={errors.category_id?.message}>
        {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
      </Select>
      <Input type="date" label="Date" {...register("date")} error={errors.date?.message} />
      <Input label="Note (optional)" {...register("note")} error={errors.note?.message} />
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Saving..." : "Save"}
      </Button>
      <Button type="button" variant="ghost" onClick={onCancel}>Cancel</Button>
    </form>
  );
}
```

### 8.9.3 Form Behavior Rules

| Rule | Implementation |
|---|---|
| Validate on blur | `mode: "onBlur"` |
| Validate on submit | Always |
| Disable submit while loading | `isSubmitting` |
| Show field-level errors | `errors.field?.message` |
| Show backend errors | Catch mutation error, map to field if `error.field` |
| Reset on success | `onSuccess()` closes modal |
| Preserve values on error | React Hook Form keeps state |

## 8.10 Design System

### 8.10.1 Colors

| Token | Value | Usage |
|---|---|---|
| `primary` | `#3B82F6` | Buttons, links, active nav |
| `primary-hover` | `#2563EB` | Button hover |
| `success` | `#22C55E` | Success toast, under budget |
| `warning` | `#EAB308` | Approaching limit |
| `danger` | `#EF4444` | Errors, over budget, delete |
| `background` | `#F9FAFB` | Page background |
| `surface` | `#FFFFFF` | Cards, modals |
| `border` | `#E5E7EB` | Card borders, dividers |
| `text-primary` | `#111827` | Headings, body |
| `text-secondary` | `#6B7280` | Labels, metadata |
| `text-muted` | `#9CA3AF` | Placeholders, disabled |

### 8.10.2 Typography

| Element | Class | Size |
|---|---|---|
| Page title | `text-2xl font-semibold` | 24px |
| Section title | `text-lg font-semibold` | 18px |
| Card title | `text-base font-medium` | 16px |
| Body | `text-sm` | 14px |
| Label | `text-sm font-medium` | 14px |
| Caption | `text-xs text-gray-500` | 12px |
| KPI value | `text-3xl font-bold` | 30px |

**Font family**: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto`

**Numbers**: `tabular-nums` for aligned digits in tables and KPIs.

### 8.10.3 Spacing

| Token | Value |
|---|---|
| Page padding | `px-6 py-8` |
| Card padding | `p-6` |
| Card gap | `gap-6` |
| Section gap | `space-y-8` |
| Form field gap | `space-y-4` |
| Max content width | `max-w-7xl mx-auto` |

### 8.10.4 Component Specifications

**Button**:

| Variant | Background | Text | Border |
|---|---|---|---|
| Primary | `bg-blue-500` | `text-white` | none |
| Secondary | `bg-white` | `text-gray-700` | `border border-gray-300` |
| Danger | `bg-red-500` | `text-white` | none |
| Ghost | transparent | `text-gray-700` | none |

Height: 40px. Padding: `px-4 py-2`. Radius: `rounded-lg`.

**Card**:

- Background: white
- Border: `border border-gray-200`
- Radius: `rounded-xl`
- Shadow: `shadow-sm`
- Padding: `p-6`

**Input**:

- Height: 40px
- Border: `border border-gray-300`
- Radius: `rounded-lg`
- Focus: `ring-2 ring-blue-500`
- Error: `border-red-500`

**Modal**:

- Overlay: `bg-black/50`
- Panel: `max-w-lg w-full bg-white rounded-xl shadow-xl`
- Position: centered
- Close: X button + Esc + overlay click
- Focus trap: enabled

**Toast**:

- Position: top-right
- Auto-dismiss: 3 seconds
- Variants: success (green), error (red), info (blue)

### 8.10.5 Chart Colors

| Chart | Colors |
|---|---|
| Pie | From category colors |
| Trend bars | `#3B82F6` |
| Cumulative line | `#3B82F6` normal, `#EF4444` over budget |
| Budget reference | `#9CA3AF` dashed |
| Heatmap | `#F3F4F6` → `#DBEAFE` → `#93C5FD` → `#3B82F6` → `#1E40AF` |
| Progress bar | green `< 80%`, yellow `80-100%`, red `> 100%` |

## 8.11 Loading, Empty, and Error States

### 8.11.1 Loading States

| Context | Component | Appearance |
|---|---|---|
| Full page (auth check) | `<FullPageSpinner />` | Centered spinner |
| Chart loading | `<Skeleton />` | Grey rectangle matching chart size |
| Table loading | Skeleton rows | 5 grey rows |
| Button submit | Inline spinner | Spinner + "Saving..." |
| KPI cards | Skeleton | Grey blocks |

### 8.11.2 Empty States

| Context | Message |
|---|---|
| No expenses this month | "No expenses this month. Add your first expense to get started." |
| No budget set | "No budget set for this month. Set one to track your spending." |
| No recent transactions | "No transactions yet." |
| No custom categories | "Using default categories. Add custom ones to personalize." |
| Filtered result empty | "No expenses match your filters." |
| Dashboard with no data | Per-chart messages; KPI cards show $0.00 |

**Empty state component**:

```tsx
// components/common/EmptyState.tsx
type Props = {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
};

export function EmptyState({ icon, title, description, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      {icon && <div className="mb-4 text-gray-400">{icon}</div>}
      <h3 className="text-base font-medium text-gray-900">{title}</h3>
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
```

### 8.11.3 Error States

| Error | UI |
|---|---|
| 401 Unauthorized | Toast + redirect to login |
| 403 Forbidden | Toast "Access denied" |
| 404 Not Found | Toast "Not found" |
| 409 Conflict | Field-level error if `error.field`, else toast |
| 422 Validation | Field-level error |
| 500 Server error | Toast "Something went wrong. Please try again." |
| Network error | Toast "Network error. Check your connection." |
| Query error | `<ErrorState />` with retry button |

**Error state component**:

```tsx
// components/common/ErrorState.tsx
type Props = {
  message?: string;
  onRetry?: () => void;
};

export function ErrorState({ message = "Failed to load", onRetry }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <p className="text-sm text-gray-500">{message}</p>
      {onRetry && (
        <Button variant="secondary" onClick={onRetry} className="mt-4">
          Try again
        </Button>
      )}
    </div>
  );
}
```

### 8.11.4 Confirm Dialog

Used before destructive actions:

```tsx
<ConfirmDialog
  open={open}
  title="Delete expense?"
  description="This action cannot be undone."
  confirmLabel="Delete"
  variant="danger"
  onConfirm={handleDelete}
  onCancel={() => setOpen(false)}
/>
```

## 8.12 Accessibility

### 8.12.1 Checklist

| Item | Implementation |
|---|---|
| Form labels | Every input has `<label htmlFor>` |
| Button text | Visible text or `aria-label` |
| Modal | `role="dialog"`, `aria-modal="true"`, focus trap, Esc closes |
| Charts | `<title>` and `<desc>` elements, or adjacent text |
| Error messages | `aria-live="polite"`, `aria-describedby` |
| Color contrast | >= 4.5:1 for text |
| Keyboard navigation | Tab order logical, no traps |
| Skip link | "Skip to main content" |
| Page titles | Unique per route |
| Language | `<html lang="en">` |
| Focus visible | `focus:ring-2` on all interactive elements |
| Icon buttons | `aria-label` describing action |

### 8.12.2 Modal Focus Management

```tsx
// On open: focus first focusable element
// On close: return focus to trigger
// Tab cycles within modal
// Esc closes modal
useEffect(() => {
  if (!open) return;
  const previous = document.activeElement as HTMLElement;
  modalRef.current?.focus();

  const handleKey = (e: KeyboardEvent) => {
    if (e.key === "Escape") onClose();
  };
  document.addEventListener("keydown", handleKey);

  return () => {
    document.removeEventListener("keydown", handleKey);
    previous?.focus();
  };
}, [open, onClose]);
```

### 8.12.3 Chart Accessibility

Each chart has:

- `<figure>` wrapper
- `<figcaption>` describing the chart
- `role="img"` with `aria-label` summarizing key values
- Data table alternative available on demand (optional)

```tsx
<figure role="img" aria-label={`Category breakdown: Food $450, Groceries $300, Transportation $200`}>
  <figcaption className="sr-only">Category breakdown for October 2026</figcaption>
  <PieChart>...</PieChart>
</figure>
```

## 8.13 Performance Optimization

### 8.13.1 Techniques

| Technique | Implementation |
|---|---|
| Code splitting | `React.lazy` for pages |
| Chart lazy loading | `React.lazy` for chart components |
| Memoization | `React.memo` for pure chart components |
| Query caching | React Query 5-minute staleTime |
| Debounced input | 300ms for filter inputs |
| Pagination | Server-side, 20 items per page |
| SVG charts | Recharts uses SVG, no canvas |
| Bundle analysis | `vite-bundle-visualizer` in development |
| Asset hashing | Vite default, long cache |
| Gzip | Vite default |

### 8.13.2 Lazy Loading

```tsx
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ExpensesPage = lazy(() => import("./pages/ExpensesPage"));
const BudgetPage = lazy(() => import("./pages/BudgetPage"));
const CategoriesPage = lazy(() => import("./pages/CategoriesPage"));

<Suspense fallback={<FullPageSpinner />}>
  <Routes>
    <Route path="/" element={<DashboardPage />} />
    ...
  </Routes>
</Suspense>
```

### 8.13.3 Performance Budget

| Metric | Target |
|---|---|
| Initial JS bundle | < 300 KB gzipped |
| Initial CSS | < 30 KB gzipped |
| Lighthouse performance | > 85 |
| First contentful paint | < 1.5s |
| Time to interactive | < 3s |

### 8.13.4 What We Do Not Optimize

- Image optimization (no images)
- Server-side rendering (SPA only)
- Service worker (not needed)
- CDN (Render provides one)
- Prefetching (React Query handles on navigation)

## 8.14 Frontend Testing

### 8.14.1 Test Structure

```
src/
├── utils/
│   ├── format.ts
│   └── format.test.ts
├── utils/
│   ├── date.ts
│   └── date.test.ts
├── utils/
│   ├── validation.ts
│   └── validation.test.ts
├── components/
│   └── charts/
│       ├── BudgetProgress.tsx
│       └── BudgetProgress.test.tsx
├── components/
│   └── forms/
│       ├── ExpenseForm.tsx
│       └── ExpenseForm.test.tsx
└── pages/
    ├── LoginPage.tsx
    └── LoginPage.test.tsx
```

### 8.14.2 Test Coverage Targets

| Area | Coverage |
|---|---|
| Utils (format, date, validation) | 90%+ |
| Chart components | 80%+ |
| Form components | 80%+ |
| Page components | 60%+ |
| API modules | Not tested (mocked) |

### 8.14.3 Test Examples

**format.test.ts**:
```ts
describe("formatUSD", () => {
  it("formats integer amounts", () => {
    expect(formatUSD("125")).toBe("$125.00");
  });
  it("formats decimal amounts", () => {
    expect(formatUSD("125.5")).toBe("$125.50");
  });
  it("formats large amounts with commas", () => {
    expect(formatUSD("1234567.89")).toBe("$1,234,567.89");
  });
  it("handles zero", () => {
    expect(formatUSD("0")).toBe("$0.00");
  });
});
```

**BudgetProgress.test.tsx**:
```tsx
describe("BudgetProgress", () => {
  it("shows green when under 80%", () => {
    render(<BudgetProgress totalSpent="500" budget="1000" percentage={50} isOverBudget={false} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-green-500");
  });
  it("shows yellow when 80-100%", () => {
    render(<BudgetProgress totalSpent="850" budget="1000" percentage={85} isOverBudget={false} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-yellow-500");
  });
  it("shows red when over budget", () => {
    render(<BudgetProgress totalSpent="1100" budget="1000" percentage={110} isOverBudget={true} />);
    expect(screen.getByRole("progressbar")).toHaveClass("bg-red-500");
  });
  it("shows 'No budget set' when budget is 0", () => {
    render(<BudgetProgress totalSpent="0" budget="0" percentage={null} isOverBudget={false} />);
    expect(screen.getByText("No budget set")).toBeInTheDocument();
  });
});
```

**ExpenseForm.test.tsx**:
```tsx
describe("ExpenseForm", () => {
  it("submits valid data", async () => {
    const onSuccess = vi.fn();
    render(<ExpenseForm onSuccess={onSuccess} onCancel={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Amount"), "125.50");
    await userEvent.selectOptions(screen.getByLabelText("Category"), "cat-1");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));

    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
  });

  it("shows error for negative amount", async () => {
    render(<ExpenseForm onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Amount"), "-50");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Amount must be positive")).toBeInTheDocument();
  });

  it("shows error for three decimal places", async () => {
    render(<ExpenseForm onSuccess={vi.fn()} onCancel={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Amount"), "125.505");
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(await screen.findByText("Invalid amount format")).toBeInTheDocument();
  });
});
```

### 8.14.4 MSW Setup

```ts
// test/mocks/handlers.ts
import { http, HttpResponse } from "msw";

export const handlers = [
  http.post("http://localhost:8000/api/v1/auth/login", () => {
    return HttpResponse.json({
      access_token: "test-token",
      token_type: "bearer",
      user: { id: "1", email: "test@example.com", username: "test", is_active: true, created_at: "2026-10-15T00:00:00Z" },
    });
  }),

  http.get("http://localhost:8000/api/v1/categories", () => {
    return HttpResponse.json({ categories: [] });
  }),
];
```

```ts
// test/mocks/server.ts
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
```

```ts
// test/setup.ts
import { beforeAll, afterEach, afterAll } from "vitest";
import { server } from "./mocks/server";

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 8.15 Frontend Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Build tool | Vite | Fast, simple, course-aligned |
| Language | TypeScript | Type safety, self-documenting |
| Styling | Tailwind CSS | Fast, consistent, no runtime |
| Charts | Recharts | React-native, composable |
| Server state | React Query | Caching, retries, invalidation |
| Client state | Context | Minimal, no Redux needed |
| Forms | React Hook Form + Zod | Minimal re-renders, shared validation |
| HTTP | Axios | Interceptors, error handling |
| Dates | date-fns | Lightweight, immutable |
| Routing | React Router v6 | Standard, nested routes |
| Token storage | localStorage | Simple; documented trade-off |
| API layer | Centralized in `src/api/` | Single integration point |
| Error handling | Interceptor + normalized errors | Consistent UX |
| Loading | Skeleton for charts, spinner for pages | Perceived performance |
| Empty states | Per-chart messages | Clear guidance |
| Dark mode | Not in MVP | Reduces scope |
| i18n | Not in MVP | English only |
| SSR | No | SPA is sufficient |
| PWA | No | Not needed for demo |
| Analytics | No | Privacy, scope |
| Accessibility | WCAG 2.1 AA for forms and navigation | Quality baseline |
| Test framework | Vitest + RTL | Vite-native, fast |
| Mocking | MSW | Network-level, realistic |
| Coverage | Not enforced | Report only |
```

---
