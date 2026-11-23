-- psql variables use identifier-safe quoting through :'variable'.
INSERT INTO lane_events (
  event_key, lane, workflow, event_type, repo, run_id, run_attempt,
  subject_url, phase_id, conclusion, head_sha, payload, occurred_at
)
VALUES (
  :'key', :'lane', :'workflow', :'event_type', :'repo',
  NULLIF(:'run_id','')::INT8, NULLIF(:'run_attempt','')::INT4,
  NULLIF(:'subject_url',''), NULLIF(:'phase_id',''),
  NULLIF(:'conclusion',''), NULLIF(:'head_sha',''),
  :'payload'::JSONB, :'occurred_at'::TIMESTAMPTZ
)
ON CONFLICT (event_key) DO NOTHING;
