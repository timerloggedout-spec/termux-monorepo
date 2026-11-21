-- Run as a CockroachDB cluster administrator while connected to defaultdb.
-- Set generated login passwords through the cluster secret manager after role creation.
CREATE DATABASE IF NOT EXISTS lane_events;
CREATE ROLE IF NOT EXISTS lane_events_writer WITH LOGIN;
CREATE ROLE IF NOT EXISTS lane_events_migrator WITH LOGIN;

REVOKE ALL ON DATABASE lane_events FROM public;
REVOKE ALL ON DATABASE lane_events FROM lane_events_writer;
REVOKE ALL ON DATABASE lane_events FROM lane_events_migrator;
GRANT CONNECT ON DATABASE lane_events TO lane_events_writer, lane_events_migrator;
