-- psql variables (quoted by psql, never interpolated by the shell):
-- key lane workflow event_type repo run_id run_attempt subject_url phase_id conclusion head_sha payload occurred_at
INSERT INTO lane_events (event_key, lane, workflow, event_type, repo, run_id, run_attempt,
                         subject_url, phase_id, conclusion, head_sha, payload, occurred_at)
VALUES (:'key', :'lane', :'workflow', :'event_type', :'repo',
        NULLIF(:'run_id','')::bigint, NULLIF(:'run_attempt','')::integer,
        NULLIF(:'subject_url',''), NULLIF(:'phase_id',''), NULLIF(:'conclusion',''), NULLIF(:'head_sha',''),
        :'payload'::jsonb, :'occurred_at'::timestamptz)
ON CONFLICT DO NOTHING;
