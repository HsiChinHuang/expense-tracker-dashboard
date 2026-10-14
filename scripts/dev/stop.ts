/**
 * npm run stop - the orphan reaper (t62, Q2).
 *
 * Scoped to the two DEV_PORTS and nothing else: an unrelated listener (the
 * ac5 control on :8799) must SURVIVE this script. Every cleaned port is
 * reported with the PID that was killed, and a run on a clean tree is
 * idempotent - it exits 0 and says so the operator can tell clean from dirty.
 */
import { DEV_PORTS, killPid, listenersByPort, platformLine } from "./common.js";

function main(): number {
  console.log(`[stop] ${platformLine()} - scoped to the dev ports ${DEV_PORTS.join(" / ")} only`);

  const byPort = listenersByPort();
  let reaped = 0;
  let failed = 0;

  for (const port of DEV_PORTS) {
    const pids = byPort.get(port);
    if (!pids || pids.length === 0) {
      console.log(`[stop] port ${port} is free - nothing to clean`);
      continue;
    }
    for (const pid of pids) {
      const rc = killPid(pid);
      if (rc === 0) {
        reaped += 1;
        console.log(`[stop] cleaned port ${port} - killed PID ${pid}`);
      } else {
        failed += 1;
        console.log(`[stop] port ${port}: killing PID ${pid} exited ${rc} - it may need a moment to exit`);
      }
    }
  }

  if (reaped === 0 && failed === 0) {
    console.log("[stop] nothing to clean - both dev ports are already free (clean tree)");
    return 0;
  }
  if (failed > 0) {
    console.log(`[stop] ${String(failed)} listener(s) could not be reaped; re-run npm run stop`);
    return 1;
  }
  console.log(`[stop] reaped ${String(reaped)} orphan listener(s) on the dev ports; no other port was touched`);
  return 0;
}

process.exit(main());
