--
-- World Cup Database (FCC Relational Databases v9, unit 039)
-- Rebuild: psql -U postgres < worldcup.sql
--

DROP DATABASE IF EXISTS worldcup;
CREATE DATABASE worldcup WITH TEMPLATE = template0 ENCODING = 'UTF8';

\connect worldcup

CREATE TABLE public.teams (
    team_id SERIAL PRIMARY KEY,
    name character varying NOT NULL UNIQUE
);

CREATE TABLE public.games (
    game_id SERIAL PRIMARY KEY,
    year integer NOT NULL,
    round character varying NOT NULL,
    winner_id integer NOT NULL REFERENCES public.teams(team_id),
    opponent_id integer NOT NULL REFERENCES public.teams(team_id),
    winner_goals integer NOT NULL,
    opponent_goals integer NOT NULL
);
