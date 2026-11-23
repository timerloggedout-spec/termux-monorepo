-- Run as a CockroachDB administrator while connected to the lane_events database.
-- Grant schema DDL to the migrator and append/read access to the runtime writer.
REVOKE ALL ON SCHEMA public FROM public;
REVOKE ALL ON SCHEMA public FROM lane_events_writer;
GRANT USAGE ON SCHEMA public TO lane_events_writer;
GRANT USAGE, CREATE ON SCHEMA public TO lane_events_migrator;

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM public;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM lane_events_writer;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO lane_events_writer;

ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA public
  REVOKE ALL ON TABLES FROM public;
ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA public
  REVOKE ALL ON TABLES FROM lane_events_writer;
ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA public
  GRANT SELECT, INSERT ON TABLES TO lane_events_writer;
