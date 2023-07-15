-- Database: postgres
CREATE TABLE Locations(
  location_id SERIAL PRIMARY KEY,
  location_name VARCHAR(255)
  longitude DECIMAL(5, 3)
  latitude DECIMAL(5,3)
  coordinates POINT
);

CREATE TABLE Forecast (
    forecast_id SERIAL PRIMARY KEY
    location_id INTEGER REFERENCES(Locations, location_id)
    day DATE
    min_temp FLOAT
    max_temp FLOAT
);

CREATE TABLE hourly_data (
    

);

-- DROP DATABASE IF EXISTS postgres;

CREATE DATABASE postgres
    WITH
    OWNER = yousefabuzahrieh
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

COMMENT ON DATABASE postgres
    IS 'default administrative connection database';