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
        self.connection = None
        self.cursor = None
        self.sql_connect(self.config)
        self.create_locations_table()

    @staticmethod
    def load_json(file):
        return json.load(open(Path(__file__).parent.absolute() / file, encoding='utf-8'))

    @staticmethod
    def config_user():
        config = ForecastDB.load_json('config.json')
        return config

    def sql_connect(self, config_):
        global weather_db
        class DBTables(NamedTuple):
            location: str
            temperature: str
            hourly: str
            weatheremoji: str
        
        weather_db = DBTables(*map(lambda i: i[i.find('('):], open(Path.cwd() / 'weather_db.sql').read().split('\n\n')))
        @dataclass
        class SqlParams:
            host: str
            database: str
            username: str
            password: str

        config = SqlParams(*config_)

        try:
            self.connection = psycopg2.connect(
                host=config.host,
                database=config.database,
                user=config.username,
                password=config.password
            )
            self.cursor = self.connection.cursor()
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"An error occurred during database connection: {e}")
            self.close_db()
            raise SystemExit

    def create_locations_table(self):
        data = self.data
        
        class LocationInfo(NamedTuple):
            location_name: str
            longitude: float
            latitude: float
            first_day: str
        
        loc_data = LocationInfo(location_name=data[0]['location'],
                                    longitude=data[0]['coordinates']['longitude'],
                                    latitude=data[0]['coordinates']['latitude'],
                                    first_day=data[0]['day']['date'])
        try:
            self.cursor.execute(f'CREATE TABLE IF NOT EXISTS locations {weather_db.location}')
            self.connection.commit()
            self.cursor.execute('INSERT INTO locations \
                                (location_name, longitude, latitude) \
                                VALUES (%s, %s, %s) RETURNING location_id', \
                                (loc_data.location_name, loc_data.longitude, loc_data.latitude))
            location_id = self.cursor.fetchone()[0]
            self.connection.commit()
            self.cursor.execute('SELECT * FROM locations')
            rows = self.cursor.fetchall()
            print('Contents of the "locations" table:')
            for row in rows:
                print(row)
        except psycopg2.errors.DuplicateTable:
            print('hello')
    
    # def create_tables(self):
    #     global table_name
    #     class ParsedDate(NamedTuple):
    #         year: int
    #         month: int
    #         day: int
        
    #     for day in range(15):
    #         date = ParsedDate(*map(lambda i: int(i), self.data[day]['day']['date'].split('-')))
    #         table_name = f"day_{date.month}_{date.day}_{date.year}"
    #         self.create_day_table()

    # def create_day_table(self):
    #     global weather_db
    #     class DBTables(NamedTuple):
    #         location: str
    #         temperature: str
    #         hourly: str
    #         weatheremoji: str
        
    #     weather_db = DBTables(*map(lambda i:  i[i.find('('):], open(Path.cwd() / 'weather_db.sql').read().split('\n\n')))
    #     self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} ( 
    #                         location_id SERIAL PRIMARY KEY,
    #                         location_name VARCHAR(255),
    #                         longitude DECIMAL(5, 3),
    #                         latitude DECIMAL(5,3)
    #                         );""")
    #     self.cursor.execute()
    #     self.connection.commit()
        # self.update_db(table_name)

    # def update_db(self,table_name):
    #     @dataclass
    #     class LocationInfo:
    #         arg1: float
    #         arg2: float
    #     try:
    #         locations = self.data[0]['coordinates']
    #         for location in range(len(self.data)):
    #             # **Locations Table**
    #             location_name = self.data[location]['location']
    #             print(location_name)
                # coordinates = LocationInfo(arg1=self.data[location]['longitude'], arg2=self.data[location]['latitude'])
                # execute_first_query = f'INSERT INTO {table_name} (location_name, longitude, latitude) VALUES (%s, %s, %s) RETURNING location_id'
                # self.cursor.execute(execute_first_query, (location_name, coordinates.arg1, coordinates.arg2))
                # location_id = self.cursor.fetchone()[0]
                
            # for day_data in self.data:
            #     # **Locations Table**
            #     location_name = day_data['location']
            #     coordinates = LocationInfo(arg1=day_data['coordinates']['longitude'], arg2=day_data['coordinates']['latitude'])
            #     execute_first_query = f'INSERT INTO {table_name} (location_name, longitude, latitude) VALUES (%s, %s, %s) RETURNING location_id'
            #     self.cursor.execute(execute_first_query, (location_name, coordinates.arg1, coordinates.arg2))
            #     location_id = self.cursor.fetchone()[0]
            #     # ** Locations Table Executed **

                # **Temperature Table**
                # date = day_data['day']['date']
                # day_data = day_data['day']
                # min_temp = LocationInfo(arg1=day_data['min_temp']['Celcius'],
                #                         arg2=day_data['min_temp']['Fahrenheit'])
                # max_temp = LocationInfo(arg1=day_data['max_temp']['Celcius'],
                #                         arg2=day_data['max_temp']['Fahrenheit'])
                # execute_second_query = 'INSERT INTO Temperature (location_id, day, min_temp_cel, min_temp_fah, max_temp_cel, max_temp_fah) VALUES (%s, %s, %s, %s, %s, %s) RETURNING temperature_id'
                # self.cursor.execute(execute_second_query, (location_id, date, min_temp.arg1, min_temp.arg2, max_temp.arg1, max_temp.arg2))
                # temperature_id = self.cursor.fetchone()[0]
                # # **Temperature Table Executed**
                
                # # Check if the temperature_id already exists in Hourly table
                # self.cursor.execute('SELECT COUNT(*) FROM Hourly WHERE temperature_id = %s', (temperature_id,))
                # count = self.cursor.fetchone()[0]

                # for hourly in day_data['hourly_data']:
                #     # **Hourly Table**
                #     hour = hourly['hour']
                #     temperature = LocationInfo(arg1=hourly['temperature']['Celcius'],
                #                             arg2=hourly['temperature']['Fahrenheit'])
                #     humidity = hourly['humidity']
                #     conditions = hourly['conditions']
                #     execute_third_query = 'INSERT INTO Hourly (temperature_id, hour, temp_cel, temp_fah, humidity, conditions) VALUES (%s, %s, %s, %s, %s, %s) RETURNING temperature_id'
                #     try:
                #         self.cursor.execute(execute_third_query, (temperature_id, hour, temperature.arg1, temperature.arg2, humidity, conditions))
                #         hourly_id = self.cursor.fetchone()[0]
                #         if temperature_id is None:
                #             temperature_id = hourly_id  # Set temperature_id on the first iteration
                #     except psycopg2.errors.UniqueViolation:
                #         # If a unique constraint violation occurs, skip the row
                #         print(f"Skipping duplicate entry for temperature_id: {temperature_id}")
                #         continue
                #     # **Hourly Table Executed**
                #     self.connection.commit()
                #     # **Weather Emoji Table**
                #     emoji = LocationInfo(arg1=hourly['emoji']['Icon Code'],
                #                         arg2=hourly['emoji']['Decoded Bytes'])
                #     execute_fourth_query = 'INSERT INTO WeatherEmoji (icon_code, bytes) VALUES (%s, %s) RETURNING emoji_id'
                #     self.cursor.execute(execute_fourth_query, (emoji.arg1, emoji.arg2))
                #     weather_emoji_id = self.cursor.fetchone()[0]
                #     # **Weather Emoji Table Executed**
        # except Exception as e:
        #     # Rollback the transaction in case of any exception
        #     self.connection.rollback()
        #     raise e
        #     print(f"An error occurred during database update. Database not affected.")

    # def get_table_contents(self):
    #     for day in range(15):
    #         self.cursor.execute(f"SELECT * FROM {table_name}")
    #         rows = self.cursor.fetchall()
    #         print(f"Contents of table {table_name}:")
    #         for row in rows:
    #             print(row)
    #         print()

    
    def close_db(self):
        if self.connection:
            try:
                self.connection.rollback()
                print("Transaction rollback completed.")
            except psycopg2.Error as e:
                print(f"An error occurred during transaction rollback: {e}")
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database Updated Successfully")
    
    def __del__(self):
        self.close_db()


def main():
    config = ForecastDB.load_json('config.json')
    sql_params = list(map(lambda i: config.get(i, ''), config))[-4:]
    weather_db = ForecastDB(sql_params)


if __name__ == '__main__':
    main()


#TODO:

# **Table: Locations**

# | location_id | location_name         | longitude | latitude |
# |-------------|-----------------------|-----------|----------|
# | 1           | New York, NY, USA     | -74.0071  | 40.7146  |

# **Table: Temperature**

# | temperature_id | location_id | date       | min_temp_cel | min_temp_fah | max_temp_cel | max_temp_fah |
# |----------------|-------------|------------|--------------|--------------|--------------|--------------|
# | 1              | 1           | 2023-07-15 | 22.3         | 72.14        | 31.6         | 88.88        |
# | 2              | 1           | 2023-07-16 | 22.3         | 72.14        | 31.6         | 88.88        |

# **Table: Hourly**

# | hourly_id | temperature_id | hour      | temp_cel | temp_fah | humidity | conditions |
# |-----------|----------------|-----------|----------|----------|----------|------------|
# | 1         | 1              | 00:00:00  | 22.8     | 73.04    | 88       | Rain       |
# | 2         | 1              | 01:00:00  | ...      | ...      | ...      | ...        |
# | ...       | ...            | ...       | ...      | ...      | ...      | ...        |
# | 25        | 1              | 23:00:00  | ...      | ...      | ...      | ...        |
# | 26        | 2              | 00:00:00  | 25.6     | 78.08    | ...      | ...        |
# | 27        | 2              | 01:00:00  | ...      | ...      | ...      | ...        |
# | ...       | ...            | ...       | ...      | ...      | ...      | ...        |
# | 48        | 2              | 23:00:00  | ...      | ...      | ...      | ...        |

# In this database structure, we have three tables: `Locations`, `Temperature`, and `Hourly`. The `Locations` table stores the location information, the `Temperature` table stores the temperature data for each day, and the `Hourly` table stores the hourly data for each day.

# The tables are related using foreign key constraints. The `temperature_id` column in the `Hourly` table references the `temperature_id` column in the `Temperature` table, and the `location_id` column in the `Temperature` table references the `location_id` column in the `Locations` table.

# By organizing the data in this relational database structure, you can efficiently store and retrieve the information related to locations, temperatures, and hourly data.