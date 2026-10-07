import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AppShell } from './app_shell';

describe('AppShell', () => {
  it('renders the application shell header', () => {
    render(<AppShell />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading.textContent).toBe('Expense Tracker');
  });

  it('applies tailwind utility classes to the shell container', () => {
    const { container } = render(<AppShell />);
    const shell = container.firstElementChild;
    expect(shell).not.toBeNull();
    expect(shell?.className).toContain('min-h-screen');
    expect(shell?.className).toContain('flex');
  });

  it('renders the main content area', () => {
    render(<AppShell />);
    const message = screen.getByText('Frontend skeleton is running.');
    expect(message.tagName).toBe('P');
  });
});
