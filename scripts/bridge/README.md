# scripts/bridge — hub + tunnel health toolkit

Three files, one purpose: verify the Pinggy/cloudflared/serveo lanes and
the :8800 hub serve real traffic.

## Commands

    scripts/bridge/bridge_health.sh local      # probe 127.0.0.1:8800
    scripts/bridge/bridge_health.sh external   # probe live tunnel.url
    scripts/bridge/bridge_health.sh add-route  # ensure GET /health on hub
    scripts/bridge/bridge_health.sh all        # route + probes + canary

## Exit codes

    0     every probe returned HTTP 200
    1     at least one probe returned a code other than 200
    2..3  configuration or syntax gate failed before probing

## Design contract

- Probes treat HTTP 200 as the sole success signal
- add-route writes once; second run reports present:true action:noop
- ast.parse gates every write
- Backups land beside server.py with a timestamp suffix
- Secrets stay out of logs
