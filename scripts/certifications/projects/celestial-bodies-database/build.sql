-- Unit 025 -- Build a Celestial Bodies Database (FCC Relational Databases v9, project)
-- Schema + data satisfying every user story in the CodeRoad story set
-- (TUTORIAL.md of freeCodeCamp/learn-celestial-bodies-database):
--   universe DB; tables galaxy/star/planet/moon (+asteroid = 5th); PK per table,
--   auto-increment, named <table>_id; name column VARCHAR in every table;
--   INT on >=2 non-key columns; NUMERIC >=1; TEXT >=1; BOOLEAN on >=2 columns;
--   star.galaxy_id -> galaxy, planet.star_id -> star, moon.planet_id -> planet;
--   rows: every table >=3, galaxy >=6, star >=6, planet >=12, moon >=20;
--   columns: every table >=3, galaxy/star/planet/moon >=5;
--   >=2 NOT NULL columns per table; >=1 UNIQUE column per table.

CREATE TABLE galaxy (
  galaxy_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  age_in_millions_of_years INT NOT NULL,
  distance_from_earth_in_light_years NUMERIC,
  description TEXT,
  has_black_hole BOOLEAN
);

CREATE TABLE star (
  star_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  age_in_millions_of_years INT NOT NULL,
  distance_in_light_years NUMERIC,
  is_visible_from_earth BOOLEAN,
  galaxy_id INT NOT NULL REFERENCES galaxy(galaxy_id)
);

CREATE TABLE planet (
  planet_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  orbital_period_in_days INT NOT NULL,
  mass_in_earths NUMERIC,
  has_life BOOLEAN NOT NULL,
  surface_description TEXT,
  star_id INT NOT NULL REFERENCES star(star_id)
);

CREATE TABLE moon (
  moon_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  diameter_in_km INT NOT NULL,
  orbital_period_in_days NUMERIC,
  is_spherical BOOLEAN,
  planet_id INT NOT NULL REFERENCES planet(planet_id)
);

CREATE TABLE asteroid (
  asteroid_id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  diameter_in_km NUMERIC NOT NULL,
  is_potentially_hazardous BOOLEAN NOT NULL
);

INSERT INTO galaxy (name, age_in_millions_of_years, distance_from_earth_in_light_years, description, has_black_hole) VALUES
  ('Milky Way', 13600, 0, 'Our home galaxy, a barred spiral containing the Solar System.', TRUE),
  ('Andromeda', 10000, 2537000, 'Nearest large spiral galaxy, on a collision course with the Milky Way.', TRUE),
  ('Triangulum', 12000, 2730000, 'Third-largest member of the Local Group.', TRUE),
  ('Whirlpool', 11300, 23000000, 'Interacting grand-design spiral galaxy.', TRUE),
  ('Sombrero', 10000, 29000000, 'Spiral galaxy with an exceptionally bright core.', TRUE),
  ('Large Magellanic Cloud', 13000, 163000, 'Satellite galaxy of the Milky Way.', FALSE);

INSERT INTO star (name, age_in_millions_of_years, distance_in_light_years, is_visible_from_earth, galaxy_id) VALUES
  ('Sun', 4600, 0, TRUE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Sirius', 242, 8.6, TRUE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Proxima Centauri', 4850, 4.2, FALSE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Betelgeuse', 10, 642, TRUE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Rigel', 8, 863, TRUE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Vega', 455, 25, TRUE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('Kepler-186', 4000, 579, FALSE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way')),
  ('TRAPPIST-1', 7600, 39, FALSE, (SELECT galaxy_id FROM galaxy WHERE name = 'Milky Way'));

INSERT INTO planet (name, orbital_period_in_days, mass_in_earths, has_life, surface_description, star_id) VALUES
  ('Mercury', 88, 0.055, FALSE, 'Cratered, airless rocky surface.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Venus', 225, 0.815, FALSE, 'Thick acidic clouds over a volcanic surface.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Earth', 365, 1, TRUE, 'Liquid-water oceans and an oxygen-rich atmosphere.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Mars', 687, 0.107, FALSE, 'Cold deserts of iron-oxide dust.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Jupiter', 4333, 317.8, FALSE, 'Gas giant with a centuries-old storm.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Saturn', 10759, 95.2, FALSE, 'Gas giant famous for its icy ring system.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Uranus', 30687, 14.5, FALSE, 'Ice giant tilted on its side.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Neptune', 60190, 17.1, FALSE, 'The windiest ice giant.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Pluto', 90560, 0.003, FALSE, 'Dwarf planet of rock and ice in the Kuiper belt.', (SELECT star_id FROM star WHERE name = 'Sun')),
  ('Proxima Centauri b', 11, 1.07, FALSE, 'Rocky planet in the habitable zone of its star.', (SELECT star_id FROM star WHERE name = 'Proxima Centauri')),
  ('Proxima Centauri c', 1928, 7, FALSE, 'Cold super-Earth far from its star.', (SELECT star_id FROM star WHERE name = 'Proxima Centauri')),
  ('Kepler-186f', 130, 1.4, FALSE, 'Earth-sized planet in the habitable zone.', (SELECT star_id FROM star WHERE name = 'Kepler-186')),
  ('TRAPPIST-1e', 6, 0.7, FALSE, 'Rocky planet, among the most likely to hold water.', (SELECT star_id FROM star WHERE name = 'TRAPPIST-1'));

INSERT INTO moon (name, diameter_in_km, orbital_period_in_days, is_spherical, planet_id) VALUES
  ('Moon', 3474, 27.3, TRUE, (SELECT planet_id FROM planet WHERE name = 'Earth')),
  ('Phobos', 22, 0.3, FALSE, (SELECT planet_id FROM planet WHERE name = 'Mars')),
  ('Deimos', 12, 1.3, FALSE, (SELECT planet_id FROM planet WHERE name = 'Mars')),
  ('Io', 3643, 1.8, TRUE, (SELECT planet_id FROM planet WHERE name = 'Jupiter')),
  ('Europa', 3122, 3.6, TRUE, (SELECT planet_id FROM planet WHERE name = 'Jupiter')),
  ('Ganymede', 5268, 7.2, TRUE, (SELECT planet_id FROM planet WHERE name = 'Jupiter')),
  ('Callisto', 4821, 16.7, TRUE, (SELECT planet_id FROM planet WHERE name = 'Jupiter')),
  ('Titan', 5150, 16, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Enceladus', 504, 1.4, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Rhea', 1527, 4.5, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Iapetus', 1469, 79.3, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Dione', 1123, 2.7, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Tethys', 1062, 1.9, TRUE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Mimas', 396, 0.9, FALSE, (SELECT planet_id FROM planet WHERE name = 'Saturn')),
  ('Titania', 1578, 8.7, TRUE, (SELECT planet_id FROM planet WHERE name = 'Uranus')),
  ('Oberon', 1523, 13.5, TRUE, (SELECT planet_id FROM planet WHERE name = 'Uranus')),
  ('Umbriel', 1169, 4.1, TRUE, (SELECT planet_id FROM planet WHERE name = 'Uranus')),
  ('Ariel', 1158, 2.5, TRUE, (SELECT planet_id FROM planet WHERE name = 'Uranus')),
  ('Triton', 2707, 5.9, TRUE, (SELECT planet_id FROM planet WHERE name = 'Neptune')),
  ('Charon', 1212, 6.4, TRUE, (SELECT planet_id FROM planet WHERE name = 'Pluto'));

INSERT INTO asteroid (name, diameter_in_km, is_potentially_hazardous) VALUES
  ('Ceres', 940, FALSE),
  ('Vesta', 525, FALSE),
  ('Pallas', 512, FALSE),
  ('Bennu', 0.49, TRUE);
