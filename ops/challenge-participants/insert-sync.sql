-- psql variables: sync ref counts events
INSERT INTO participant_syncs (sync_key, source_ref, counts, events)
VALUES (:'sync', :'ref', :'counts'::jsonb, :'events'::jsonb)
ON CONFLICT DO NOTHING;
