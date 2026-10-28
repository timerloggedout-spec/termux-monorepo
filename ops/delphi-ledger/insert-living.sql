-- psql variables: vkey record issue sha snapshot body
INSERT INTO delphi_living_records (version_key, record_id, issue_number,
                                   body_sha256, snapshot_at, body)
VALUES (:'vkey', :'record', :'issue'::integer, :'sha',
        NULLIF(:'snapshot','')::timestamptz, :'body')
ON CONFLICT DO NOTHING;
