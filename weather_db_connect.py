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
        self.create_tables()

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
            clocation: str
            ctemperature: str
            chourly: str
            cweatheremoji: str
        
        # weather_db = DBTables(*map(lambda i: i[i.find('('):], open(Path.cwd() / 'weather_db.sql').read().split('\n\n')))
        weather_db = DBTables(*open(Path.cwd() / 'weather_db.sql').read().split('\n\n')[:4])
        @dataclass
        class SQLParams:
            host: str
            database: str
            username: str
            password: str

        config = SQLParams(*config_)
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

    def create_tables(self):
        
        try:
            self.cursor.execute(weather_db.clocation)
            self.connection.commit()
            
            self.cursor.execute(weather_db.ctemperature)
            self.connection.commit()
            
            self.cursor.execute(weather_db.chourly)
            self.connection.commit()
            
            self.cursor.execute(weather_db.cweatheremoji)
            self.connection.commit()
            
            self.insert_tables()
            
        except psycopg2.errors.DuplicateTable:
            print('Table already exists')
    
    def insert_tables(self):
        data = self.data
        class SQLData(NamedTuple):
            arg1: str=None
            arg2: float|str=None
            arg3: float|str=None
            arg4: str=None
            arg5: str=None
            arg6: str=None

        def dataclass_mapper(attr, endpoint):
            return  (*map(lambda i: getattr(attr, f'arg{i}'), range(1, endpoint+1)),)
        
        loca_data = SQLData(arg1=data[0]['location'],
                            arg2=data[0]['coordinates']['longitude'],
                            arg3=data[0]['coordinates']['latitude'])
        location_data = dataclass_mapper(loca_data, 3)
        self.cursor.execute('INSERT INTO Locations (location_name, longitude, latitude) \
                            VALUES (%s, %s, %s) \
                            RETURNING location_id',
                            (*location_data,))
        location_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        for i in range(15):
            temp_data = SQLData(arg1=location_id,
                                arg2=data[i]['day']['date'],
                                arg3=data[i]['day']['min_temp']['Celcius'],
                                arg4=data[i]['day']['min_temp']['Fahrenheit'],
                                arg5=data[i]['day']['max_temp']['Celcius'],
                                arg6=data[i]['day']['max_temp']['Fahrenheit'])
            temperature_data = dataclass_mapper(temp_data, 6)
            self.cursor.execute('INSERT INTO Temperature (location_id, day, min_temp_cel, \
                                                        min_temp_fah, max_temp_cel, max_temp_fah) \
                                VALUES (%s, %s, %s, %s, %s, %s) \
                                RETURNING temperature_id',
                                (*temperature_data,))
            temperature_id = self.cursor.fetchone()[0]
            self.connection.commit()


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