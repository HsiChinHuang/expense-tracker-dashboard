import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from './app';
import { AuthProvider } from './context/auth_context';
import { ToastProvider } from './context/toast_context';
import './index.css';

const queryClient = new QueryClient();

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Root element #root not found');
}

const root = createRoot(rootElement);

// Provider nesting per REQ-ARCH-013: QueryClientProvider -> BrowserRouter ->
// AuthProvider -> ToastProvider -> App. MonthProvider arrives with later
// phases and may be inserted between Auth and Toast.
root.render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <App />
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
