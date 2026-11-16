-- psql variables (quoted by psql, never interpolated by the shell):
-- key ledger issue comment marker payload body occurred
INSERT INTO delphi_ledger_events (event_key, ledger_id, issue_number, comment_id,
                                  marker, payload, body, occurred_at)
VALUES (:'key', :'ledger', :'issue'::integer, :'comment'::bigint,
        NULLIF(:'marker',''), NULLIF(:'payload','')::jsonb, :'body', :'occurred'::timestamptz)
ON CONFLICT DO NOTHING;
