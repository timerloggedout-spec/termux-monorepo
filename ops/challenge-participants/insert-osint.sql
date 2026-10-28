-- psql variables: key sync event payload
INSERT INTO osint_page_snapshots (snapshot_key, sync_key, event_id, payload)
VALUES (:'key', :'sync', :'event', :'payload'::jsonb)
ON CONFLICT DO NOTHING;
