--
-- Periodic Table Database (FCC Relational Databases v9, unit 062)
-- Final state of the course database after the Part 1 fixes.
-- Rebuild: psql -U postgres < periodic_table.sql
--

DROP DATABASE IF EXISTS periodic_table;
CREATE DATABASE periodic_table WITH TEMPLATE = template0 ENCODING = 'UTF8';

\connect periodic_table

CREATE TABLE public.types (
    type_id integer PRIMARY KEY,
    type character varying NOT NULL
);

INSERT INTO public.types VALUES (1, 'nonmetal'), (2, 'metal'), (3, 'metalloid');

CREATE TABLE public.elements (
    atomic_number integer PRIMARY KEY,
    symbol character varying(2) UNIQUE NOT NULL,
    name character varying(40) UNIQUE NOT NULL
);

INSERT INTO public.elements VALUES
    (1, 'H', 'Hydrogen'),
    (2, 'He', 'Helium'),
    (3, 'Li', 'Lithium'),
    (4, 'Be', 'Beryllium'),
    (5, 'B', 'Boron'),
    (6, 'C', 'Carbon'),
    (7, 'N', 'Nitrogen'),
    (8, 'O', 'Oxygen'),
    (9, 'F', 'Fluorine'),
    (10, 'Ne', 'Neon');

CREATE TABLE public.properties (
    atomic_number integer PRIMARY KEY REFERENCES public.elements(atomic_number),
    atomic_mass numeric NOT NULL,
    melting_point_celsius numeric NOT NULL,
    boiling_point_celsius numeric NOT NULL,
    type_id integer NOT NULL REFERENCES public.types(type_id)
);

INSERT INTO public.properties VALUES
    (1, 1.008, -259.1, -252.9, 1),
    (2, 4.0026, -272.2, -269, 1),
    (3, 6.94, 180.54, 1342, 2),
    (4, 9.0122, 1287, 2470, 2),
    (5, 10.81, 2075, 4000, 3),
    (6, 12.011, 3550, 4027, 1),
    (7, 14.007, -210.1, -195.8, 1),
    (8, 15.999, -218, -183, 1),
    (9, 18.998, -220, -188.1, 1),
    (10, 20.18, -248.6, -246.1, 1);
