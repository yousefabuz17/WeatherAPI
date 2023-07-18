import json
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import psycopg2



class SQLParams(NamedTuple):
    host: str
    database: str
    username: str
    password: str
@dataclass
class DBTables:
    clocation: str
    ctemperature: str
    chourly: str
    cweatheremoji: str
    ilocation: str
    itemperature: str
    ihourly: str
    iweatheremoji: str
@dataclass
class SQLData:
    arg1: str=None
    arg2: float|str=None
    arg3: float|str=None
    arg4: str=None
    arg5: str=None
    arg6: str=None


class ForecastDB:
    def __init__(self, config: list):
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
        self.days = 15
        self.config = config
        self.connection = None
        self.cursor = None
        self.sql_connect(self.config)
        self.create_tables()

    @staticmethod
    def load_json(file):
        return json.load(open(Path(__file__).parent.absolute() / file, encoding='utf-8'))

    @staticmethod
    def get_config():
        return ForecastDB.load_json('config.json')

    def sql_connect(self, config_):
        global weather_db
        
        weather_db = DBTables(*open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[:8]) #All SQL create table scripts
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

        def dataclass_mapper(attr, endpoint):
            return  (*map(lambda i: getattr(attr, f'arg{i}'), range(1, endpoint+1)),)
        
        #**Executing Locations Table**
        loca_data = SQLData(arg1=data[0]['location'],
                            arg2=data[0]['coordinates']['longitude'],
                            arg3=data[0]['coordinates']['latitude'])
        location_data = dataclass_mapper(loca_data, 3)
        self.cursor.execute(weather_db.ilocation,
                            (*location_data,))
        location_id = self.cursor.fetchone()[0]
        self.connection.commit()
        #** Locations Table Executed**
        
            #**Executing Temperature Table**
        for i in range(self.days):
            temp_data = SQLData(arg1=location_id,
                                arg2=data[i]['day']['date'],
                                arg3=data[i]['day']['min_temp']['Celcius'],
                                arg4=data[i]['day']['min_temp']['Fahrenheit'],
                                arg5=data[i]['day']['max_temp']['Celcius'],
                                arg6=data[i]['day']['max_temp']['Fahrenheit'])
            temperature_data = dataclass_mapper(temp_data, 6)
            self.cursor.execute(weather_db.itemperature,
                                (*temperature_data,))
            temperature_id = self.cursor.fetchone()[0]
            self.connection.commit()
            #**Temperature Table Executed**
            
            #**Executing WeatherEmoji Table**
            emoji_d = data[i]['day']['hourly_data']
            emoji = SQLData(arg1=emoji_d[i]['emoji']['Icon Code'],
                            arg2=emoji_d[i]['emoji']['Decoded Bytes'])
            emoji_data = dataclass_mapper(emoji, 2)
            self.cursor.execute(weather_db.iweatheremoji,
                                (*emoji_data,))
            emoji_id = self.cursor.fetchone()[0]
            self.connection.commit()
            #** WeatherEmoji Table Executed**
        
        #**Executing Hourly Table**
        hour_data = data[i]['day']['hourly_data']
        for j in range(24):  # Iterate over 24 hours
            hourly = SQLData(
                arg1=temperature_id,
                arg2=hour_data[j]['hour'],
                arg3=hour_data[j]['temperature']['Celcius'],
                arg4=hour_data[j]['temperature']['Fahrenheit'],
                arg5=hour_data[j]['humidity'],
                arg6=hour_data[j]['conditions']
            )
            hourly_data = dataclass_mapper(hourly, 6)
            self.cursor.execute(weather_db.ihourly,
                                (*hourly_data,))
            hourly_id = self.cursor.fetchone()[0]
            self.connection.commit()
        #** Hourly Table Executed**

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
    config = list(ForecastDB.get_config().values())[-4:]
    weather_db = ForecastDB(config)


if __name__ == '__main__':
    main()
