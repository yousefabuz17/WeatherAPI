import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import psycopg2
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder

from weather_data import WeatherForecast


class SQLParams(NamedTuple):
    host: str
    database: str
    user: str
    password: str


class SQLFetch(NamedTuple):
    arg1: str


@dataclass
class Args:
    arg1: str
    arg2: str


class DBConnect:
    def __init__(self, sql_script=None):
        self.sql_script = sql_script
        self.connection = None
        self.cursor = None
        self.database = None
        self.validator()

    def sql_connect(self):
        config = SQLParams(*list(WeatherForecast.get_config().values())[-4:])
        try:
            with psycopg2.connect(
                                host=config.host,
                                database=config.database,
                                user=config.user,
                                password=config.password
                                ) as self.connection:
                self.cursor = self.connection.cursor()
                self.database = self.query_data()
        except (psycopg2.Error, FileNotFoundError) as e:
            raise e
            print(f"An error occurred during database connection: {e}")
            raise SystemExit

    def query_data(self):
        columns = self.get_columns(self.sql_script.arg1)
        execute_ = self.sql_script.arg1
        self.cursor.execute(execute_)
        rows = self.cursor.fetchall()
        col_data = Args(arg1=rows, arg2=columns)
        return col_data #**Returns full database including columns
    
    def __repr__(self): #**Returns full database in a DataFrame
        try:
            rows = self.database.arg1
            columns = self.database.arg2
            df = pd.DataFrame(rows, columns=columns)
            return df.__repr__()  # For demonstration purposes
        except AttributeError:
            return 'No database found'

    def validator(self):
        try: self.sql_connect()
        except AttributeError: return 'No database found'

    def group_location(self, id_=None): #? Predictive testing for each location
        columns = self.get_columns(self.sql_script.arg1)
        sql_script = f'{self.sql_script.arg1[:-1]}\nWHERE l.location_id = \'{id_}\''
        self.cursor.execute(sql_script)
        rows = self.cursor.fetchall()
        data = Args(arg1=rows, arg2=columns)
        df = pd.DataFrame(data.arg1, columns=data.arg2)
        return df
    
    @staticmethod
    def get_columns(sql):
        #**Fetching columns based on script rather hard coding for practice
        return filter(lambda i: not i.endswith('id') and 's' not in i, map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql)))

    def __del__(self):
        if self.cursor:
            self.cursor.close()


def main():
    sql_script = SQLFetch(open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[-1])
    database = DBConnect()
    print(database)


if __name__ == '__main__':
    main()
