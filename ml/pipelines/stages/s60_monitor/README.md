# Stage 60_monitor — MONITOR

Watch post-merge Actions; feed WAIT → VALIDATE → RE-FETCH.

Halt policy: FAILED stops the DAG. SKIPPED is allowed when inputs are empty.
