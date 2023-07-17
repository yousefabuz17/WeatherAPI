import json
import psycopg2
import seaborn as sns
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple
from weather_data import WeatherForecast
from weather_db_connect import DBTables


class SQLParams(NamedTuple):
    host: str=None
    database: str=None
    user: str=None
    password: str=None

class DBConnect:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def sql_connect(self):
        global sql_script
        sql_script = DBTables(*open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n'))
        
        try:
            self.connection = psycopg2.connect(
                                host=config.host,
                                database=config.database,
                                user=config.user,
                                password=config.password)
            self.cursor = self.connection.cursor()
            
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"An error occurred during database connection: {e}")
            self.close_db()
            raise SystemExit
    
    def query_data(self):
        pass
    
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
    global config
    get_config = list(WeatherForecast.get_config().values())[-4:]
    config = SQLParams(*get_config)
    DBConnect().sql_connect()


if __name__ == '__main__':
    main()