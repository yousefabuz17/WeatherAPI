-- Database: postgres
CREATE TABLE Locations(
  location_id SERIAL PRIMARY KEY,
  location_name VARCHAR(255)
  longitude DECIMAL(5, 3)
  latitude DECIMAL(5,3)
  coordinates POINT
);

CREATE table Forecast(
    forecast_id SERIAL PRIMARY KEY
    location_forecast_id INTEGER REFERENCES Locations(location_id)
    day DATE
    min_temp_cel DECIMAL(4,2)
    min_temp_fah DECIMAL(4,2)
    max_temp_cel DECIMAL(4,2)
    max_temp_fah DECIMAL(4,2)
);

CREATE TABLE Hourly(
    hourly_data_id SERIAL PRIMARY KEY
    forecast_locaation_id INTEGER REFERENCES Forecast(location_forecast_id)
    hour TIME
    temp_cel DECIMAL(4,2)
    temp_fah DECIMAL(4,2)
    humidity INTEGER
    conditions VARCHAR(255)
    weather_icon_code VARCHAR(255)
    bytes BYTEA
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