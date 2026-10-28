-- psql variables: key sync event participant payload
INSERT INTO participant_events (event_key, sync_key, event_id, participant_key, payload)
VALUES (:'key', :'sync', :'event', :'participant', :'payload'::jsonb)
ON CONFLICT DO NOTHING;
