# Stage 50_deploy — DEPLOY

Emit promote packets only when repo_gate + termux_smoke are green.

Halt policy: FAILED stops the DAG. SKIPPED is allowed when inputs are empty.
