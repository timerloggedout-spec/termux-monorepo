--
-- Salon Appointment Scheduler (FCC Relational Databases v9, unit 040)
-- Rebuild: psql -U postgres < salon.sql
--

DROP DATABASE IF EXISTS salon;
CREATE DATABASE salon WITH TEMPLATE = template0 ENCODING = 'UTF8';

\connect salon

CREATE TABLE public.customers (
    customer_id SERIAL PRIMARY KEY,
    name character varying,
    phone character varying UNIQUE
);

CREATE TABLE public.services (
    service_id SERIAL PRIMARY KEY,
    name character varying
);

CREATE TABLE public.appointments (
    appointment_id SERIAL PRIMARY KEY,
    customer_id integer REFERENCES public.customers(customer_id),
    service_id integer REFERENCES public.services(service_id),
    time character varying
);

INSERT INTO public.services (name) VALUES ('cut'), ('color'), ('perm'), ('style'), ('trim');
