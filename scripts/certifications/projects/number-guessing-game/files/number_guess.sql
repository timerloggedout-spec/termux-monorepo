--
-- Number Guessing Game (FCC Relational Databases v9, unit 063)
-- Rebuild: psql -U postgres < number_guess.sql
--

DROP DATABASE IF EXISTS number_guess;
CREATE DATABASE number_guess WITH TEMPLATE = template0 ENCODING = 'UTF8';

\connect number_guess

CREATE TABLE public.users (
    user_id SERIAL PRIMARY KEY,
    username character varying(22) UNIQUE NOT NULL
);

CREATE TABLE public.games (
    game_id SERIAL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES public.users(user_id),
    guesses integer NOT NULL
);
