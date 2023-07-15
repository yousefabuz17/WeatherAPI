import json
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
import psycopg2


class ForecastDB:
    def __init__(self, sql_params: list):
        """
    Initialize the class with SQL connection parameters.
    
    Parameter:
        - `sql_params` (list): A list containing the following SQL connection parameter contents:
            - `host` (str): The hostname or IP address of the database server.
            - `database` (str): The name of the database to connect to.
            - `user` (str): The username to authenticate with.
            - `password` (str): The password for the specified user.
        """
        self.data = ForecastDB.load_json('Forecast_data.json')
        self.config = sql_params
        self.sql_connect(self.config)

    @staticmethod
    def load_json(file):
        """
        Load JSON data from a file.

        Parameters:
        - `file` (str): The path to the JSON file.

        Returns:
        - The loaded JSON data.
        """
        return json.load(open(Path(__file__).parent.absolute() / file, encoding='utf-8'))

    @staticmethod
    def config_user():
        """
        Load database configuration parameters from the 'config.json' file.

        Returns:
        - The loaded database configuration parameters.
        """
        config = ForecastDB.load_json('config.json')
        return config

    def sql_connect(self, config_):
        """
        Connect to the PostgreSQL database using the provided configuration parameters.

        Parameters:
        - `config_` (list): A list of SQL connection parameters.

        Raises:
        - `psycopg2.Error`: If an error occurs during the database connection.
        - `FileNotFoundError`: If the 'config.json' file is not found.
        """
        global connection, cursor

        @dataclass
        class SqlParams:
            host: str
            database: str
            user: str
            password: str

        config = SqlParams(*config_)

        try:
            connection = psycopg2.connect(
                host=config.host,
                database=config.database,
                user=config.user,
                password=config.password
            )
            cursor = connection.cursor()
            self.create_tables()
            self.update_db(self.data)
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"An error occurred during database connection: {e}")
            self.close_db()
            raise SystemExit

    def create_tables(self):
        """
        Create the necessary database tables.

        This method creates the tables for storing temperature data for each day and hour.

        Raises:
        - `psycopg2.Error`: If an error occurs during table creation.
        """
        class ParsedDate(NamedTuple):
            year: int
            month: int
            day: int
        
        for day in range(15):
            date = ParsedDate(*list(map(lambda i: int(i), self.data[day]['date'].split('-'))))
            table_name = f"Day_{date.month}_{date.day}_{date.year}"
            self.create_day_table(table_name)
            for hour in range(24):
                hour_table_name = f"{table_name}_Hour_{hour:02d}"
                self.create_hour_table(hour_table_name)

    def create_day_table(self, table_name):
        """
        Create a table for storing temperature data for a specific day.

        Parameters:
        - `table_name` (str): The name of the table to be created.

        Raises:
        - `psycopg2.Error`: If an error occurs during table creation.
        """
        global weather_db
        class DBTables(NamedTuple):
            location: str
            temperature: str
            hourly: str
            weatheremoji: str
        
        weather_db = DBTables(*list(map(lambda i:  i[i.find('('):], open(Path.cwd() / 'weather_db.sql').read().split('\n\n'))))
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f"{weather_db.temperature}")

    def create_hour_table(self, table_name):
        """
        Create a table for storing temperature data for a specific hour.

        Parameters:
        - `table_name` (str): The name of the table to be created.

        Raises:
        - `psycopg2.Error`: If an error occurs during table creation.
        """
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name}"
                        f"{weather_db.hourly}")

    def update_db(self, data):
        """
        Update the database with the weather data.

        This method populates the database with the weather data retrieved from the JSON file.

        Parameters:
        - `data` (list): The weather data to be updated in the database.

        Raises:
        - `psycopg2.Error`: If an error occurs during database update.
        """
        @dataclass
        class LocationInfo:
            arg1: float
            arg2: float
        try:
            for day_data in data:
                # **Locations Table**
                location_name = day_data['location']
                coordinates = LocationInfo(arg1=day_data['coordinates']['longitude'], arg2=day_data['coordinates']['latitude'])
                execute_first_query = 'INSERT INTO Locations (location_name, longitude, latitude) VALUES (%s, %s, %s) RETURNING location_id'
                cursor.execute(execute_first_query, (location_name, coordinates.arg1, coordinates.arg2))
                location_id = cursor.fetchone()[0]
                # ** Locations Table Executed **

                # **Temperature Table**
                date = day_data['date']
                min_temp = LocationInfo(arg1=day_data['min_temp']['Celcius'],
                                        arg2=day_data['min_temp']['Fahrenheit'])
                max_temp = LocationInfo(arg1=day_data['max_temp']['Celcius'],
                                        arg2=day_data['max_temp']['Fahrenheit'])
                execute_second_query = 'INSERT INTO Temperature (location_id, day, min_temp_cel, min_temp_fah, max_temp_cel, max_temp_fah) VALUES (%s, %s, %s, %s, %s, %s) RETURNING temperature_id'
                cursor.execute(execute_second_query, (location_id, date, min_temp.arg1, min_temp.arg2, max_temp.arg1, max_temp.arg2))
                temperature_id = cursor.fetchone()[0]
                # **Temperature Table Executed**
                
                # Check if the temperature_id already exists in Hourly table
                cursor.execute('SELECT COUNT(*) FROM Hourly WHERE temperature_id = %s', (temperature_id,))
                count = cursor.fetchone()[0]

                for hourly in day_data['hourly_data']:
                    # **Hourly Table**
                    hour = hourly['hour']
                    temperature = LocationInfo(arg1=hourly['temperature']['Celcius'],
                                            arg2=hourly['temperature']['Fahrenheit'])
                    humidity = hourly['humidity']
                    conditions = hourly['conditions']
                    execute_third_query = 'INSERT INTO Hourly (temperature_id, hour, temp_cel, temp_fah, humidity, conditions) VALUES (%s, %s, %s, %s, %s, %s) RETURNING temperature_id'
                    try:
                        cursor.execute(execute_third_query, (temperature_id, hour, temperature.arg1, temperature.arg2, humidity, conditions))
                        hourly_id = cursor.fetchone()[0]
                        if temperature_id is None:
                            temperature_id = hourly_id  # Set temperature_id on the first iteration
                    except psycopg2.errors.UniqueViolation:
                        # If a unique constraint violation occurs, skip the row
                        print(f"Skipping duplicate entry for temperature_id: {temperature_id}")
                        continue
                    # **Hourly Table Executed**
                    connection.commit()
                    # **Weather Emoji Table**
                    emoji = LocationInfo(arg1=hourly['emoji']['Icon Code'],
                                        arg2=hourly['emoji']['Decoded Bytes'])
                    execute_fourth_query = 'INSERT INTO WeatherEmoji (icon_code, bytes) VALUES (%s, %s) RETURNING emoji_id'
                    cursor.execute(execute_fourth_query, (emoji.arg1, emoji.arg2))
                    weather_emoji_id = cursor.fetchone()[0]
                    # **Weather Emoji Table Executed**
        except Exception as e:
            # Rollback the transaction in case of any exception
            connection.rollback()
            print(f"An error occurred during database update. Database not affected.")

    def close_db(self):
        """
        Close the database connection and rollback any pending transaction.
        """
        if connection:
            try:
                connection.rollback()
                print("Transaction rollback completed.")
            except psycopg2.Error as e:
                print(f"An error occurred during transaction rollback: {e}")
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Database Updated Successfully")
    
    def __del__(self):
        self.close_db()


def main():
    config = ForecastDB.load_json('config.json')
    sql_params = list(map(lambda i: config.get(i, ''), config))[-4:]
    weather_db = ForecastDB(sql_params)


if __name__ == '__main__':
    main()
