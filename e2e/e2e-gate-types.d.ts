// Hermetic typecheck surface for the e2e workspace (t27 ac5, review_plan W5).
//
// The ac5 gate runs `tsc --noEmit --skipLibCheck -p e2e/tsconfig.json` with
// ZERO installs (only the root 5.3.3 / frontend 5.5.4 compilers exist), so
// the real @playwright/test package and the Node globals are NOT resolvable
// here. This declaration file closes exactly that gap by DECLARATION, not
// suppression: TS2307 (cannot find module '@playwright/test') and
// TS2580/TS2591 (`process`) cannot appear at all, because the only surface
// that would raise them is declared locally - while every real mistake
// (TS1005 syntax, TS2307 wrong local import path, TS2322 bad assignment,
// TS2304 undefined name, TS2345 wrong fixture argument) still fails the
// gate, which is what the ac5 broken-fixture leg proves.
//
// SCOPE NOTE (out-of-scope clause of t27): this is a hermetic syntax/shape
// surface ONLY. Real-API Playwright type checking happens in CI, where
// e2e/package.json installs the genuine @playwright/test 1.58.0 package.

declare module '@playwright/test' {
  /** Minimal locator surface used by the specs and fixtures. */
  export interface Locator {
    click(): Promise<void>;
    fill(value: string): Promise<void>;
    press(key: string): Promise<void>;
    selectOption(value: string): Promise<void>;
    inputValue(): Promise<string>;
    textContent(): Promise<string | null>;
    getAttribute(name: string): Promise<string | null>;
    count(): Promise<number>;
    all(): Promise<Locator[]>;
    first(): Locator;
    last(): Locator;
    nth(index: number): Locator;
    getByRole(role: string, options?: { name?: string | RegExp }): Locator;
    getByLabel(text: string | RegExp): Locator;
    getByTestId(testId: string): Locator;
    getByText(text: string | RegExp): Locator;
  }

  /** Minimal APIRequestContext surface used by the category-id resolver. */
  export interface APIResponse {
    status(): number;
    json(): Promise<unknown>;
  }

  /** Minimal page surface used by the specs and fixtures. */
  export interface Page {
    goto(url: string): Promise<void>;
    getByRole(role: string, options?: { name?: string | RegExp }): Locator;
    getByLabel(text: string | RegExp): Locator;
    getByTestId(testId: string): Locator;
    getByText(text: string | RegExp): Locator;
    evaluate<T>(expression: () => T): Promise<T>;
    requestGet(url: string, options?: { headers?: Record<string, string> }): Promise<APIResponse>;
  }

  /** Minimal browser surface (isolation.spec opens two contexts). */
  export interface BrowserContext {
    newPage(): Promise<Page>;
    close(): Promise<void>;
  }

  export interface Browser {
    newContext(): Promise<BrowserContext>;
  }

  /** Minimal expect surface (assertions the specs actually run). */
  export interface PlaywrightMatchers {
    toBeVisible(): Promise<void>;
    toHaveText(text: string | RegExp): Promise<void>;
    toHaveValue(value: string): Promise<void>;
    toHaveCount(count: number): Promise<void>;
  }

  export interface PlaywrightExpect {
    (value: Locator): PlaywrightMatchers;
    (value: string): { toBe(expected: string): Promise<void> };
  }

  export interface TestArgs {
    page: Page;
    browser: Browser;
  }

  type TestFn = (title: string, body: (args: TestArgs) => Promise<void>) => void;

  interface TestStepFn {
    (title: string, body: () => Promise<void>): Promise<void>;
  }

  /** Minimal config surface - defineConfig is an identity pass-through. */
  export interface PlaywrightConfig {
    testDir?: string;
    timeout?: number;
    retries?: number;
    workers?: number;
    reporter?: unknown;
    use?: Record<string, unknown>;
  }

  export function defineConfig(config: PlaywrightConfig): PlaywrightConfig;

  export const test: TestFn & { describe: TestFn; step: TestStepFn };
  export const expect: PlaywrightExpect;
}

declare var process: {
  env: { [key: string]: string | undefined };
};
