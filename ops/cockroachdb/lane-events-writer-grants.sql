-- Run as a CockroachDB cluster/database administrator before schema migration.
-- Isolate the lane-event ledger and grant each runtime identity least privilege.
-- Set generated login passwords through the cluster secret manager after role creation.
CREATE DATABASE IF NOT EXISTS lane_events;
CREATE ROLE IF NOT EXISTS lane_events_writer WITH LOGIN;
CREATE ROLE IF NOT EXISTS lane_events_migrator WITH LOGIN;

REVOKE ALL ON DATABASE lane_events FROM public;
GRANT CONNECT ON DATABASE lane_events TO lane_events_writer, lane_events_migrator;

REVOKE ALL ON SCHEMA lane_events.public FROM public;
GRANT USAGE ON SCHEMA lane_events.public TO lane_events_writer;
GRANT USAGE, CREATE ON SCHEMA lane_events.public TO lane_events_migrator;

REVOKE ALL ON ALL TABLES IN SCHEMA lane_events.public FROM public;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA lane_events.public TO lane_events_writer;
REVOKE UPDATE, DELETE ON ALL TABLES IN SCHEMA lane_events.public FROM lane_events_writer;

ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA lane_events.public
  REVOKE ALL ON TABLES FROM public;
ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA lane_events.public
  GRANT SELECT, INSERT ON TABLES TO lane_events_writer;
ALTER DEFAULT PRIVILEGES FOR ROLE lane_events_migrator IN SCHEMA lane_events.public
  REVOKE UPDATE, DELETE ON TABLES FROM lane_events_writer;
