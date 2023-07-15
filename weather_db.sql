CREATE TABLE Locations(
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(255),
    longitude DECIMAL(5, 3),
    latitude DECIMAL(5,3)
);

CREATE TABLE Temperature(
    temperature_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES Locations(location_id),
    day DATE,
    min_temp_cel DECIMAL(4,2),
    min_temp_fah DECIMAL(4,2),
    max_temp_cel DECIMAL(4,2),
    max_temp_fah DECIMAL(4,2)
);

CREATE TABLE Hourly(
    hourly_id SERIAL PRIMARY KEY,
    temperature_id INTEGER REFERENCES Temperature(temperature_id),
    hour TIME,
    temp_cel DECIMAL(4,2),
    temp_fah DECIMAL(4,2),
    humidity INTEGER,
    conditions VARCHAR(255),
    UNIQUE (temperature_id)
);

CREATE Table WeatherEmoji(
    emoji_id SERIAL PRIMARY KEY,
    icon_code VARCHAR(255),
    bytes BYTEA
);