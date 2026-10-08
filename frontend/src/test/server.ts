// Shared MSW server for jsdom tests. onUnhandledRequest: 'error' makes an
// unexpected network call a hard test failure (t9 constraint).

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
