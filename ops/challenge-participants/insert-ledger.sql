-- psql variables: key sync entry payload
INSERT INTO opportunity_ledger_entries (entry_key, sync_key, entry_id, payload)
VALUES (:'key', :'sync', :'entry', :'payload'::jsonb)
ON CONFLICT DO NOTHING;
