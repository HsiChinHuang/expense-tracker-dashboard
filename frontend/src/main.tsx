import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './app';
import { AuthProvider } from './context/auth_context';
import { MonthProvider } from './context/month_context';
import { ToastProvider } from './context/toast_context';
import './index.css';

const queryClient = new QueryClient();

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element #root not found');
}

const root = createRoot(rootElement);

// Provider nesting per REQ-ARCH-013 (additive): QueryClientProvider ->
// BrowserRouter -> AuthProvider -> MonthProvider -> ToastProvider -> App.
// MonthProvider (REQ-FE-032, t20) is inserted exactly between Auth and Toast
// as the merged comment promised; nothing is reordered or removed.
root.render(
  <StrictMode>
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
  </StrictMode>
);
