/**
 * npm run setup:local - repair a bare tree (t62, Q5/Q6/W8).
 *
 * Q6: a missing backend/.venv, backend/dev.db or frontend/node_modules is
 * REBUILT, not reported and skipped. Q5: additive-only - it never writes an env
 * file that does not already exist and never edits a tracked file (hence
 * `uv sync --frozen` and a no-save npm install fallback). W8: it self-reports
 * `elapsed=<seconds>` so an over-budget run is visible in the artifact.
 */
import { existsSync } from "node:fs";
import path from "node:path";
import {
  IS_WIN32,
  backendDir,
  capture,
  frontendDir,
  frontendInstalled,
  npmInvocation,
  repoRoot,
  run,
  venvPresent,
  venvPython,
} from "./common.js";

const START = Date.now();

function elapsedSeconds(): number {
  return Math.round((Date.now() - START) / 1000);
}

function ok(step: string): void {
  console.log(`[setup:local] ${step} ok (${elapsedSeconds()}s)`);
}

function fail(step: string, detail: string): never {
  console.error(`[setup:local] ${step} FAILED after ${elapsedSeconds()}s: ${detail}`);
  process.exit(1);
}

/** backend/.venv - win32-native when this script runs natively on win32 (Q1). */
function ensureVenv(): void {
  if (venvPresent()) {
    console.log("[setup:local] backend/.venv already present - reusing it (Q6 repair-without-destruction)");
    return;
  }
  console.log("[setup:local] backend/.venv missing - creating it with uv sync --frozen");
  const rc = run("uv", ["sync", "--frozen"], backendDir());
  if (!venvPresent()) {
    fail("backend/.venv", `uv sync exited ${rc} and no pyvenv.cfg exists`);
  }
  const probe = capture(venvPython(), ["-c", "import sys;print(sys.platform)"], backendDir());
  ok(`backend/.venv created (python reports sys.platform=${probe.out.trim() || "unknown"})`);
}

/** backend/dev.db - created and migrated to the single alembic head. */
function ensureDatabase(): void {
  const db = path.join(backendDir(), "dev.db");
  if (existsSync(db)) {
    console.log("[setup:local] backend/dev.db already present - reusing it");
  } else {
    console.log("[setup:local] backend/dev.db missing - creating and migrating it");
  }
  const rc = run(venvPython(), ["-m", "alembic", "upgrade", "head"], backendDir());
  if (rc !== 0) {
    fail("backend/dev.db", `alembic upgrade head exited ${rc}`);
  }
  const cur = capture(venvPython(), ["-m", "alembic", "current"], backendDir());
  ok(`backend/dev.db migrated (alembic current: ${cur.out.split(/\r?\n/).filter(Boolean).join(" ") || "no output"})`);
}

/** frontend/node_modules - installed and usable. */
function ensureFrontend(): void {
  if (frontendInstalled()) {
    console.log("[setup:local] frontend/node_modules already present - reusing it");
    return;
  }
  const lock = path.join(frontendDir(), "package-lock.json");
  const args = existsSync(lock)
    ? ["ci", "--no-audit", "--no-fund"]
    : ["install", "--no-save", "--no-package-lock", "--no-audit", "--no-fund"];
  console.log(`[setup:local] frontend/node_modules missing - npm ${args[0] ?? "install"} (Q5 additive-only: no manifest writes)`);
  const npm = npmInvocation(args);
  const rc = run(npm.cmd, npm.args, frontendDir());
  if (!frontendInstalled()) {
    fail("frontend/node_modules", `npm ${args[0] ?? "install"} exited ${rc} and no vite binary exists`);
  }
  ok("frontend/node_modules installed");
}

function main(): number {
  console.log(`[setup:local] platform=${process.platform} native=${IS_WIN32 ? "yes" : "no"} root=${repoRoot()}`);
  ensureVenv();
  ensureDatabase();
  ensureFrontend();
  const elapsed = elapsedSeconds();
  console.log(`[setup:local] environment ready - budget is 600s (W8), elapsed=${elapsed}`);
  return 0;
}

process.exit(main());
