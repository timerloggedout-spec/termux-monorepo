-- psql variables: sync ref counts
INSERT INTO participant_syncs (sync_key, source_ref, counts)
VALUES (:'sync', :'ref', :'counts'::jsonb)
ON CONFLICT DO NOTHING;
