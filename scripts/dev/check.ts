/**
 * npm run check - detect and report the environment state (t62, Q1/Q4/Q6).
 *
 * Q1: the SAME npm script runs natively on win32 and says which platform it is on.
 * Q4: an occupied port is REPORTED with its owning PID and never touched.
 * Q6: host toolchain / venv / frontend-deps state is reported, not guessed at.
 */
import {
  DEV_PORTS,
  IS_WIN32,
  backendDir,
  frontendDir,
  frontendInstalled,
  listenersByPort,
  capture,
  platformLine,
  venvPresent,
} from "./common.js";

/** Host tools the workflow needs; reported, never installed by `check`. */
const HOST_TOOLS: readonly string[] = ["node", "npm", "uv", "git"];

function toolVersion(tool: string): string {
  const r = capture(tool, ["--version"]);
  if (r.code === 127) {
    return "MISSING (not on PATH)";
  }
  const first = r.out.split(/\r?\n/)[0] ?? "";
  return r.code === 0 ? first.trim() : `present but exited ${r.code}`;
}

function main(): number {
  const problems: string[] = [];

  console.log(`[check] ${platformLine()} (node ${process.version})`);

  // --- host toolchain (Q6: detect-and-report, never silently guess) ---------
  for (const tool of HOST_TOOLS) {
    console.log(`[check] host tool ${tool}: ${toolVersion(tool)}`);
  }
  if (!IS_WIN32) {
    console.log("[check] note: not running natively on win32; the Linux/WSL path is the Makefile");
  }

  // --- ports (Q4: report the port AND the owning PID, touch nothing) --------
  const byPort = listenersByPort();
  console.log(`[check] TCP listeners currently visible: ${byPort.size} port(s)`);
  for (const [port, pids] of [...byPort.entries()].sort((a, b) => a[0] - b[0])) {
    const owned = DEV_PORTS.includes(port) ? " (dev port)" : "";
    console.log(`[check] occupied port ${port}${owned} owned by PID ${pids.join(",")} - reported only, not touched`);
  }
  for (const port of DEV_PORTS) {
    if (byPort.has(port)) {
      problems.push(`dev port ${port} is already in use - free it (or run npm run stop) before npm run dev`);
    }
  }

  // --- backend venv (Q6: repair without destruction happens in setup:local) -
  if (venvPresent()) {
    console.log(`[check] backend/.venv present at ${backendDir()} - left untouched`);
  } else {
    problems.push("backend/.venv missing - run npm run setup:local to build it");
  }

  // --- frontend deps --------------------------------------------------------
  if (frontendInstalled()) {
    console.log(`[check] frontend dependencies present at ${frontendDir()}`);
  } else {
    problems.push("frontend/node_modules missing - run npm run setup:local to install it");
  }

  if (problems.length > 0) {
    console.log(`[check] ${problems.length} thing(s) need attention:`);
    for (const p of problems) {
      console.log(`[check] - ${p}`);
    }
    console.log("[check] details above; npm run setup:local performs the repairs");
    return 1;
  }
  console.log("[check] environment is ready - dev ports free, venv and frontend deps present");
  return 0;
}

process.exit(main());
