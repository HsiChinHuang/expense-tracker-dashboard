import { afterAll, afterEach, beforeAll, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './server';

// MSW lifecycle: one server for the whole process, per-test handler
// overrides still apply via server.use(...). Unhandled requests error.
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  localStorage.clear();
  vi.restoreAllMocks();
});

afterAll(() => {
  server.close();
});
