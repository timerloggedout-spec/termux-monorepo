# Hindsight Database Access

## Ground truth

The Postgres instance is pg0-embedded and lives ONLY on the codespace at:

    /home/vscode/.pg0/instances/hindsight/instance.json

Fields (literal, no rotation):

    username: hindsight
    password: hindsight
    database: hindsight
    port:     5432
    version:  18.1.0
    data_dir: /home/vscode/.pg0/instances/hindsight/data

`pg_hba.conf` uses `password` auth on local, 127.0.0.1, and ::1.

## Two audiences

### Codespace-local scripts
Direct PG. Source these:

    INST=/home/vscode/.pg0/instances/hindsight/instance.json
    PGHOST=/tmp
    PGPORT=5432
    PGUSER=hindsight
    PGPASSWORD=hindsight
    PGDATABASE=hindsight
    PSQL=/home/vscode/.pg0/installation/18.1.0/bin/psql

### Termux-side scripts / agents
Do NOT have /home/vscode/.pg0. Talk to Hindsight over HTTP:
`$HINDSIGHT_BASE_URL` + `Authorization: Bearer $HINDSIGHT_API_KEY`.

## DO statements
- DO run PG queries from the codespace, not Termux.
- DO read credentials from instance.json (never hardcode in git).
- DO NOT trust API /banks fact_count for live reads. It lags.
  Query banks.fact_count directly for truth.
