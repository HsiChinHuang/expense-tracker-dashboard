/**
 * npm run dev - run the whole environment (t62, Q1/Q2).
 *
 * Spawns the backend (uvicorn on :8000) and the frontend (vite on :5173) as
 * native children of the CURRENT platform, prefixes every child line with
 * `[backend]` / `[frontend]` so one interleaved log stays readable, prints the
 * URLs the operator should click, and tears both children down on SIGINT and
 * SIGTERM. On win32 a real console Ctrl+C cannot be delivered from an
 * automated harness, so `npm run stop` is the guaranteed reaper either way.
 */
import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import {
  DEV_PORTS,
  IS_WIN32,
  backendDir,
  frontendDir,
  listenersByPort,
  platformLine,
  venvPresent,
  venvPython,
} from "./common.js";

const BACKEND_URL = "http://localhost:8000";
const FRONTEND_URL = "http://localhost:5173";

const children: ChildProcess[] = [];
let stopping = false;

/** Stream a child's stdout+stderr through a readable prefix. */
function prefixed(child: ChildProcess, tag: string): void {
  const pipe = (stream: NodeJS.ReadableStream): void => {
    let buffer = "";
    stream.setEncoding("utf8");
    stream.on("data", (chunk: string) => {
      buffer += chunk;
      const lines = buffer.split(/\r?\n/);
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        console.log(`[${tag}] ${line}`);
      }
    });
  };
  if (child.stdout) {
    pipe(child.stdout);
  }
  if (child.stderr) {
    pipe(child.stderr);
  }
}

function startBackend(): ChildProcess | null {
  if (!venvPresent()) {
    console.log("[backend] backend/.venv is missing - run npm run setup:local first");
    return null;
  }
  const c = spawn(venvPython(), ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], {
    cwd: backendDir(),
    stdio: ["ignore", "pipe", "pipe"],
  });
  prefixed(c, "backend");
  children.push(c);
  return c;
}

function startFrontend(): ChildProcess | null {
  const viteJs = path.join(frontendDir(), "node_modules", "vite", "bin", "vite.js");
  if (!existsSync(viteJs)) {
    console.log("[frontend] frontend/node_modules/vite is missing - run npm run setup:local first");
    return null;
  }
  const c = spawn(process.execPath, [viteJs], {
    cwd: frontendDir(),
    stdio: ["ignore", "pipe", "pipe"],
    env: { ...process.env, FORCE_COLOR: "0" },
  });
  prefixed(c, "frontend");
  children.push(c);
  return c;
}

function stopChildren(): void {
  if (stopping) {
    return;
  }
  stopping = true;
  for (const c of children) {
    if (c.exitCode === null && !c.killed) {
      console.log(`[dev] stopping child pid ${String(c.pid)}`);
      c.kill(IS_WIN32 ? undefined : "SIGTERM");
    }
  }
}

function main(): void {
  console.log(`[dev] ${platformLine()}`);

  const occupied = listenersByPort();
  const clashes = DEV_PORTS.filter((p) => occupied.has(p));
  if (clashes.length > 0) {
    for (const port of clashes) {
      console.log(`[dev] port ${port} is already in use by PID ${(occupied.get(port) ?? []).join(",")} - run npm run stop first`);
    }
    process.exit(1);
  }

  const backend = startBackend();
  const frontend = startFrontend();
  if (!backend || !frontend) {
    stopChildren();
    process.exit(1);
  }

  console.log(`[dev] backend  ${BACKEND_URL}  (API: ${BACKEND_URL}/api/v1/health)`);
  console.log(`[dev] frontend ${FRONTEND_URL}  (vite /api proxy -> ${BACKEND_URL})`);
  console.log("[dev] both servers are up - Ctrl+C in this console, or npm run stop from another one");

  // The graceful-teardown contract (Q2): BOTH handlers registered by name.
  // ac4 pins this at the source level because win32 cannot deliver a real
  // console Ctrl+C to this harness; `npm run stop` is the reaper either way.
  process.on("SIGINT", () => {
    console.log("[dev] received SIGINT - tearing down both servers");
    stopChildren();
  });
  process.on("SIGTERM", () => {
    console.log("[dev] received SIGTERM - tearing down both servers");
    stopChildren();
  });

  // Stay alive: the child stdout/stderr streams keep the event loop running.
  // Exiting here would orphan both servers, so `stop` is what reaps them.
  let pending = children.length;
  for (const c of children) {
    c.on("exit", (code, signal) => {
      console.log(`[dev] a child exited (code=${String(code)} signal=${String(signal)})`);
      pending -= 1;
      if (pending <= 0) {
        process.exit(0);
      }
    });
  }
}

main();
