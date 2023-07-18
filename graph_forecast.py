import json
import re
import psycopg2
import pandas as pd
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from pathlib import Path
from typing import NamedTuple
from weather_data import WeatherForecast


class SQLParams(NamedTuple):
    host: str
    database: str
    user: str
    password: str

class SQLFetch(NamedTuple):
    hour_temp: str

@dataclass
class Args:
    arg1: str
    arg2: str

class DBConnect:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def sql_connect(self):
        global sql_script
        sql_script = SQLFetch(open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[-1])
        
        try:
            self.connection = psycopg2.connect(
                                host=config.host,
                                database=config.database,
                                user=config.user,
                                password=config.password)
            self.cursor = self.connection.cursor()
            self.query_data()
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"An error occurred during database connection: {e}")
            self.close_db()
            raise SystemExit
    
    
    def query_data(self):
        columns = DBConnect.get_columns(sql_script.hour_temp)
        execute_ = sql_script.hour_temp
        self.cursor.execute(execute_)
        data = self.cursor.fetchall()
        col_data = Args(arg1=columns, arg2=data)
        self.linear_regression(col_data)
        return col_data
    
    def linear_regression(self,col_data):
        df = pd.DataFrame(col_data.arg2, columns=col_data.arg1)
        print(df)
    
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
    
    @staticmethod
    def get_columns(sql):
        return list(i for i in map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql)) if not i.endswith('id'))
        
    
    def __del__(self):
        self.close_db()
        
    
    

# class Regression:
#     def __init__(self):
#         pass
    
#     def linear_regression(self):
#         # col_data = DBConnect().query_data()
#         df = pd.DataFrame(col_data.arg2, columns=col_data.arg1)
#         print(df)
        



def main():
    global config
    get_config = list(WeatherForecast.get_config().values())[-4:]
    config = SQLParams(*get_config)
    sql_db = DBConnect().sql_connect()


if __name__ == '__main__':
    main()