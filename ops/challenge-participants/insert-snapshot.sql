-- psql variables: key sync kind event entity snapshot
INSERT INTO entity_snapshots (snapshot_key, sync_key, entity_kind, event_id, entity_key, snapshot)
VALUES (:'key', :'sync', :'kind', :'event', :'entity', :'snapshot'::jsonb)
ON CONFLICT DO NOTHING;
