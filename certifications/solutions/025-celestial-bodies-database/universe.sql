--
-- PostgreSQL database dump
--

\restrict 4a9prz5Kz2ffVKeb9ltxFdyHHRBbahI4gqLK14wFbB8utvNg7zWYl6n3fhgK4As

-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP DATABASE universe;
--
-- Name: universe; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE universe WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';


ALTER DATABASE universe OWNER TO postgres;

\unrestrict 4a9prz5Kz2ffVKeb9ltxFdyHHRBbahI4gqLK14wFbB8utvNg7zWYl6n3fhgK4As
\connect universe
\restrict 4a9prz5Kz2ffVKeb9ltxFdyHHRBbahI4gqLK14wFbB8utvNg7zWYl6n3fhgK4As

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asteroid; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asteroid (
    asteroid_id integer NOT NULL,
    name character varying(100) NOT NULL,
    diameter_in_km numeric NOT NULL,
    is_potentially_hazardous boolean NOT NULL
);


ALTER TABLE public.asteroid OWNER TO postgres;

--
-- Name: asteroid_asteroid_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asteroid_asteroid_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asteroid_asteroid_id_seq OWNER TO postgres;

--
-- Name: asteroid_asteroid_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asteroid_asteroid_id_seq OWNED BY public.asteroid.asteroid_id;


--
-- Name: galaxy; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.galaxy (
    galaxy_id integer NOT NULL,
    name character varying(100) NOT NULL,
    age_in_millions_of_years integer NOT NULL,
    distance_from_earth_in_light_years numeric,
    description text,
    has_black_hole boolean
);


ALTER TABLE public.galaxy OWNER TO postgres;

--
-- Name: galaxy_galaxy_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.galaxy_galaxy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.galaxy_galaxy_id_seq OWNER TO postgres;

--
-- Name: galaxy_galaxy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.galaxy_galaxy_id_seq OWNED BY public.galaxy.galaxy_id;


--
-- Name: moon; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.moon (
    moon_id integer NOT NULL,
    name character varying(100) NOT NULL,
    diameter_in_km integer NOT NULL,
    orbital_period_in_days numeric,
    is_spherical boolean,
    planet_id integer NOT NULL
);


ALTER TABLE public.moon OWNER TO postgres;

--
-- Name: moon_moon_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.moon_moon_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.moon_moon_id_seq OWNER TO postgres;

--
-- Name: moon_moon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.moon_moon_id_seq OWNED BY public.moon.moon_id;


--
-- Name: planet; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planet (
    planet_id integer NOT NULL,
    name character varying(100) NOT NULL,
    orbital_period_in_days integer NOT NULL,
    mass_in_earths numeric,
    has_life boolean NOT NULL,
    surface_description text,
    star_id integer NOT NULL
);


ALTER TABLE public.planet OWNER TO postgres;

--
-- Name: planet_planet_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planet_planet_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planet_planet_id_seq OWNER TO postgres;

--
-- Name: planet_planet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planet_planet_id_seq OWNED BY public.planet.planet_id;


--
-- Name: star; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.star (
    star_id integer NOT NULL,
    name character varying(100) NOT NULL,
    age_in_millions_of_years integer NOT NULL,
    distance_in_light_years numeric,
    is_visible_from_earth boolean,
    galaxy_id integer NOT NULL
);


ALTER TABLE public.star OWNER TO postgres;

--
-- Name: star_star_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.star_star_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.star_star_id_seq OWNER TO postgres;

--
-- Name: star_star_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.star_star_id_seq OWNED BY public.star.star_id;


--
-- Name: asteroid asteroid_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asteroid ALTER COLUMN asteroid_id SET DEFAULT nextval('public.asteroid_asteroid_id_seq'::regclass);


--
-- Name: galaxy galaxy_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.galaxy ALTER COLUMN galaxy_id SET DEFAULT nextval('public.galaxy_galaxy_id_seq'::regclass);


--
-- Name: moon moon_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.moon ALTER COLUMN moon_id SET DEFAULT nextval('public.moon_moon_id_seq'::regclass);


--
-- Name: planet planet_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planet ALTER COLUMN planet_id SET DEFAULT nextval('public.planet_planet_id_seq'::regclass);


--
-- Name: star star_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.star ALTER COLUMN star_id SET DEFAULT nextval('public.star_star_id_seq'::regclass);


--
-- Data for Name: asteroid; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.asteroid VALUES (1, 'Ceres', 940, false);
INSERT INTO public.asteroid VALUES (2, 'Vesta', 525, false);
INSERT INTO public.asteroid VALUES (3, 'Pallas', 512, false);
INSERT INTO public.asteroid VALUES (4, 'Bennu', 0.49, true);


--
-- Data for Name: galaxy; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.galaxy VALUES (1, 'Milky Way', 13600, 0, 'Our home galaxy, a barred spiral containing the Solar System.', true);
INSERT INTO public.galaxy VALUES (2, 'Andromeda', 10000, 2537000, 'Nearest large spiral galaxy, on a collision course with the Milky Way.', true);
INSERT INTO public.galaxy VALUES (3, 'Triangulum', 12000, 2730000, 'Third-largest member of the Local Group.', true);
INSERT INTO public.galaxy VALUES (4, 'Whirlpool', 11300, 23000000, 'Interacting grand-design spiral galaxy.', true);
INSERT INTO public.galaxy VALUES (5, 'Sombrero', 10000, 29000000, 'Spiral galaxy with an exceptionally bright core.', true);
INSERT INTO public.galaxy VALUES (6, 'Large Magellanic Cloud', 13000, 163000, 'Satellite galaxy of the Milky Way.', false);


--
-- Data for Name: moon; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.moon VALUES (1, 'Moon', 3474, 27.3, true, 3);
INSERT INTO public.moon VALUES (2, 'Phobos', 22, 0.3, false, 4);
INSERT INTO public.moon VALUES (3, 'Deimos', 12, 1.3, false, 4);
INSERT INTO public.moon VALUES (4, 'Io', 3643, 1.8, true, 5);
INSERT INTO public.moon VALUES (5, 'Europa', 3122, 3.6, true, 5);
INSERT INTO public.moon VALUES (6, 'Ganymede', 5268, 7.2, true, 5);
INSERT INTO public.moon VALUES (7, 'Callisto', 4821, 16.7, true, 5);
INSERT INTO public.moon VALUES (8, 'Titan', 5150, 16, true, 6);
INSERT INTO public.moon VALUES (9, 'Enceladus', 504, 1.4, true, 6);
INSERT INTO public.moon VALUES (10, 'Rhea', 1527, 4.5, true, 6);
INSERT INTO public.moon VALUES (11, 'Iapetus', 1469, 79.3, true, 6);
INSERT INTO public.moon VALUES (12, 'Dione', 1123, 2.7, true, 6);
INSERT INTO public.moon VALUES (13, 'Tethys', 1062, 1.9, true, 6);
INSERT INTO public.moon VALUES (14, 'Mimas', 396, 0.9, false, 6);
INSERT INTO public.moon VALUES (15, 'Titania', 1578, 8.7, true, 7);
INSERT INTO public.moon VALUES (16, 'Oberon', 1523, 13.5, true, 7);
INSERT INTO public.moon VALUES (17, 'Umbriel', 1169, 4.1, true, 7);
INSERT INTO public.moon VALUES (18, 'Ariel', 1158, 2.5, true, 7);
INSERT INTO public.moon VALUES (19, 'Triton', 2707, 5.9, true, 8);
INSERT INTO public.moon VALUES (20, 'Charon', 1212, 6.4, true, 9);


--
-- Data for Name: planet; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.planet VALUES (1, 'Mercury', 88, 0.055, false, 'Cratered, airless rocky surface.', 1);
INSERT INTO public.planet VALUES (2, 'Venus', 225, 0.815, false, 'Thick acidic clouds over a volcanic surface.', 1);
INSERT INTO public.planet VALUES (3, 'Earth', 365, 1, true, 'Liquid-water oceans and an oxygen-rich atmosphere.', 1);
INSERT INTO public.planet VALUES (4, 'Mars', 687, 0.107, false, 'Cold deserts of iron-oxide dust.', 1);
INSERT INTO public.planet VALUES (5, 'Jupiter', 4333, 317.8, false, 'Gas giant with a centuries-old storm.', 1);
INSERT INTO public.planet VALUES (6, 'Saturn', 10759, 95.2, false, 'Gas giant famous for its icy ring system.', 1);
INSERT INTO public.planet VALUES (7, 'Uranus', 30687, 14.5, false, 'Ice giant tilted on its side.', 1);
INSERT INTO public.planet VALUES (8, 'Neptune', 60190, 17.1, false, 'The windiest ice giant.', 1);
INSERT INTO public.planet VALUES (9, 'Pluto', 90560, 0.003, false, 'Dwarf planet of rock and ice in the Kuiper belt.', 1);
INSERT INTO public.planet VALUES (10, 'Proxima Centauri b', 11, 1.07, false, 'Rocky planet in the habitable zone of its star.', 3);
INSERT INTO public.planet VALUES (11, 'Proxima Centauri c', 1928, 7, false, 'Cold super-Earth far from its star.', 3);
INSERT INTO public.planet VALUES (12, 'Kepler-186f', 130, 1.4, false, 'Earth-sized planet in the habitable zone.', 7);
INSERT INTO public.planet VALUES (13, 'TRAPPIST-1e', 6, 0.7, false, 'Rocky planet, among the most likely to hold water.', 8);


--
-- Data for Name: star; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.star VALUES (1, 'Sun', 4600, 0, true, 1);
INSERT INTO public.star VALUES (2, 'Sirius', 242, 8.6, true, 1);
INSERT INTO public.star VALUES (3, 'Proxima Centauri', 4850, 4.2, false, 1);
INSERT INTO public.star VALUES (4, 'Betelgeuse', 10, 642, true, 1);
INSERT INTO public.star VALUES (5, 'Rigel', 8, 863, true, 1);
INSERT INTO public.star VALUES (6, 'Vega', 455, 25, true, 1);
INSERT INTO public.star VALUES (7, 'Kepler-186', 4000, 579, false, 1);
INSERT INTO public.star VALUES (8, 'TRAPPIST-1', 7600, 39, false, 1);


--
-- Name: asteroid_asteroid_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asteroid_asteroid_id_seq', 4, true);


--
-- Name: galaxy_galaxy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.galaxy_galaxy_id_seq', 6, true);


--
-- Name: moon_moon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.moon_moon_id_seq', 20, true);


--
-- Name: planet_planet_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planet_planet_id_seq', 13, true);


--
-- Name: star_star_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.star_star_id_seq', 8, true);


--
-- Name: asteroid asteroid_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asteroid
    ADD CONSTRAINT asteroid_name_key UNIQUE (name);


--
-- Name: asteroid asteroid_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asteroid
    ADD CONSTRAINT asteroid_pkey PRIMARY KEY (asteroid_id);


--
-- Name: galaxy galaxy_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.galaxy
    ADD CONSTRAINT galaxy_name_key UNIQUE (name);


--
-- Name: galaxy galaxy_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.galaxy
    ADD CONSTRAINT galaxy_pkey PRIMARY KEY (galaxy_id);


--
-- Name: moon moon_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.moon
    ADD CONSTRAINT moon_name_key UNIQUE (name);


--
-- Name: moon moon_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.moon
    ADD CONSTRAINT moon_pkey PRIMARY KEY (moon_id);


--
-- Name: planet planet_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planet
    ADD CONSTRAINT planet_name_key UNIQUE (name);


--
-- Name: planet planet_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planet
    ADD CONSTRAINT planet_pkey PRIMARY KEY (planet_id);


--
-- Name: star star_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.star
    ADD CONSTRAINT star_name_key UNIQUE (name);


--
-- Name: star star_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.star
    ADD CONSTRAINT star_pkey PRIMARY KEY (star_id);


--
-- Name: moon moon_planet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.moon
    ADD CONSTRAINT moon_planet_id_fkey FOREIGN KEY (planet_id) REFERENCES public.planet(planet_id);


--
-- Name: planet planet_star_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planet
    ADD CONSTRAINT planet_star_id_fkey FOREIGN KEY (star_id) REFERENCES public.star(star_id);


--
-- Name: star star_galaxy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.star
    ADD CONSTRAINT star_galaxy_id_fkey FOREIGN KEY (galaxy_id) REFERENCES public.galaxy(galaxy_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4a9prz5Kz2ffVKeb9ltxFdyHHRBbahI4gqLK14wFbB8utvNg7zWYl6n3fhgK4As

