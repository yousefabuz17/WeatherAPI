CREATE TABLE IF NOT EXISTS Locations (
    location_id SERIAL PRIMARY KEY,
    location_name VARCHAR(255) UNIQUE,
    longitude DECIMAL(6, 4),
    latitude DECIMAL(6, 4)
);

CREATE TABLE IF NOT EXISTS Temperature (
    temperature_id SERIAL PRIMARY KEY,
    location_id INTEGER,
    day DATE,
    min_temp_cel DECIMAL(5, 2),
    min_temp_fah DECIMAL(5, 2),
    max_temp_cel DECIMAL(5, 2),
    max_temp_fah DECIMAL(5, 2),
    FOREIGN KEY (location_id) REFERENCES Locations (location_id)
);

CREATE TABLE IF NOT EXISTS Hourly (
    hourly_id SERIAL PRIMARY KEY,
    temperature_id INTEGER,
    hour TIME,
    temp_cel DECIMAL(5, 2),
    temp_fah DECIMAL(5, 2),
    humidity INTEGER,
    conditions VARCHAR(255),
    FOREIGN KEY (temperature_id) REFERENCES Temperature (temperature_id)
);

CREATE TABLE IF NOT EXISTS WeatherEmoji (
    emoji_id SERIAL PRIMARY KEY,
    icon_code VARCHAR(255),
    bytes BYTEA
);

INSERT INTO Locations (location_name, longitude, latitude)
VALUES (%s, %s, %s)
RETURNING location_id;

INSERT INTO Temperature (location_id, day, min_temp_cel, min_temp_fah, max_temp_cel, max_temp_fah)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING temperature_id;

INSERT INTO Hourly (temperature_id, hour, temp_cel, temp_fah, humidity, conditions)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING hourly_id;

INSERT INTO WeatherEmoji (icon_code, bytes)
VALUES (%s, %s)
RETURNING emoji_id;

SELECT t.day, t.min_temp_cel, t.min_temp_fah, t.max_temp_cel, t.max_temp_fah,
        h.hour, h.temp_cel, h.temp_fah, h.humidity, h.conditions
FROM Temperature t
JOIN Hourly h ON t.temperature_id = h.temperature_id;