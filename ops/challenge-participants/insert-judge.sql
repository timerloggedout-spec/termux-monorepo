-- psql variables: key sync event judge payload
INSERT INTO judge_events (event_key, sync_key, event_id, judge_key, payload)
VALUES (:'key', :'sync', :'event', :'judge', :'payload'::jsonb)
ON CONFLICT DO NOTHING;
