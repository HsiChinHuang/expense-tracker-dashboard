/**
 * Shared helpers for the ROOT npm dev workflow (t62).
 *
 * Windows-11-first: every function here has a native win32 path (netstat for
 * the port scan, taskkill for the reaper, Scripts/python.exe for the venv) and
 * a POSIX fallback so the SAME npm script also runs on Linux. node builtins
 * only - no new dependencies (Q2).
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const IS_WIN32: boolean = process.platform === "win32";

/** The two ports the dev workflow owns. The reaper is scoped to these ONLY. */
export const DEV_PORTS: readonly number[] = [8000, 5173];

export interface Listener {
  readonly port: number;
  readonly pid: string;
}

const HERE: string = path.dirname(fileURLToPath(import.meta.url));

export function repoRoot(): string {
  return path.resolve(HERE, "..", "..");
}

export function backendDir(): string {
  return path.join(repoRoot(), "backend");
}

export function frontendDir(): string {
  return path.join(repoRoot(), "frontend");
}

export function venvDir(): string {
  return path.join(backendDir(), ".venv");
}

export function venvPython(): string {
  return IS_WIN32
    ? path.join(venvDir(), "Scripts", "python.exe")
    : path.join(venvDir(), "bin", "python");
}

export function venvPresent(): boolean {
  return existsSync(path.join(venvDir(), "pyvenv.cfg"));
}

export function frontendInstalled(): boolean {
  const bin = IS_WIN32
    ? path.join(frontendDir(), "node_modules", ".bin", "vite.cmd")
    : path.join(frontendDir(), "node_modules", ".bin", "vite");
  return existsSync(bin) || existsSync(path.join(frontendDir(), "node_modules", "vite"));
}

/** Run a child to completion with inherited stdio; returns its exit code. */
export function run(cmd: string, args: readonly string[], cwd: string): number {
  const r = spawnSync(cmd, [...args], { cwd, stdio: "inherit" });
  if (r.error) {
    console.error(`[dev-workflow] cannot start ${cmd}: ${r.error.message}`);
    return 127;
  }
  return r.status ?? 1;
}

export interface Captured {
  readonly code: number;
  readonly out: string;
}

/** Run a child capturing stdout+stderr as text. */
export function capture(cmd: string, args: readonly string[], cwd?: string): Captured {
  const r = spawnSync(cmd, [...args], { cwd, encoding: "utf8" });
  if (r.error) {
    return { code: 127, out: r.error.message };
  }
  return { code: r.status ?? 1, out: `${r.stdout ?? ""}${r.stderr ?? ""}` };
}

function portOf(addr: string): number {
  const i = addr.lastIndexOf(":");
  if (i < 0) {
    return -1;
  }
  const n = Number(addr.slice(i + 1));
  return Number.isFinite(n) ? n : -1;
}

function parseNetstat(text: string): Listener[] {
  const found: Listener[] = [];
  for (const line of text.split(/\r?\n/)) {
    const cols = line.trim().split(/\s+/);
    if (cols[0] !== "TCP" || cols.length < 5) {
      continue;
    }
    if (cols[3] !== "LISTENING") {
      continue;
    }
    const port = portOf(cols[1] ?? "");
    const pid = cols[cols.length - 1] ?? "";
    if (port > 0 && /^[0-9]+$/.test(pid)) {
      found.push({ port, pid });
    }
  }
  return found;
}

function parseSs(text: string): Listener[] {
  const found: Listener[] = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.startsWith("LISTEN")) {
      continue;
    }
    const cols = line.trim().split(/\s+/);
    const port = portOf(cols[3] ?? "");
    const m = /pid=(\d+)/.exec(line);
    if (port > 0 && m && m[1]) {
      found.push({ port, pid: m[1] });
    }
  }
  return found;
}

/** All TCP listeners visible to the OS, native to the running platform. */
export function listeners(): Listener[] {
  if (IS_WIN32) {
    // No "-p tcp" filter: that form hides IPv6 listeners in some builds.
    return parseNetstat(capture("netstat", ["-ano"]).out);
  }
  return parseSs(capture("ss", ["-ltnp"]).out);
}

/** Listeners grouped by port, de-duplicated per port (IPv4 + IPv6 share a pid). */
export function listenersByPort(): Map<number, string[]> {
  const map = new Map<number, string[]>();
  for (const l of listeners()) {
    const pids = map.get(l.port) ?? [];
    if (!pids.includes(l.pid)) {
      pids.push(l.pid);
    }
    map.set(l.port, pids);
  }
  return map;
}

/** Kill one pid (and its tree) natively for the current platform. */
export function killPid(pid: string): number {
  if (IS_WIN32) {
    return capture("taskkill", ["/PID", pid, "/F", "/T"]).code;
  }
  const r = capture("kill", ["-9", pid]);
  return r.code;
}

/** A single readable platform line, pinned by ac2: platform=<os> native=<yes|no>. */
export function platformLine(): string {
  return `platform=${process.platform} native=${IS_WIN32 ? "yes" : "no"}`;
}
