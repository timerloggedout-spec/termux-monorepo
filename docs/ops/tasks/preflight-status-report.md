# Task: preflight status report

Produce a status report on the current GPG/agent preflight state.

## Required steps

1. `read_file` on `~/deepcli/deepcli/_v1_preflight.py` — understand the
   `env_state()` and `env_risk()` functions.

2. `run` a Python one-liner that imports the module and prints env state:

       python3 -c "import sys; sys.path.insert(0,'/data/data/com.termux/files/home/deepcli'); from deepcli._v1_preflight import env_state, env_risk; s=env_state(); e,w=env_risk(s); print('state:',s); print('risk:',e,w)"

3. `write_file` to `~/.deepcli/agent_workspaces/preflight-status.md` with
   exactly these sections:

       # Preflight status — <UTC timestamp>
       ## Environment
       - agent_grips: <n>
       - pubring_size: <bytes>
       - pass_2fa_exists: <bool>
       ## Risk
       - env_score: <int>
       - breakdown: <dict>
       ## Interpretation
       <one short paragraph: is it safe to run destructive gpg operations?>

4. `finish` with a summary that names the written file and states the
   env_score value.
