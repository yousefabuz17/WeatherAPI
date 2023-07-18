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
    def __init__(self):
        self.connection = None
        self.cursor = None

    def sql_connect(self, sql_script):
        config = SQLParams(*list(WeatherForecast.get_config().values())[-4:])
        try:
            with psycopg2.connect(
                                host=config.host,
                                database=config.database,
                                user=config.user,
                                password=config.password
                                ) as self.connection:
                self.cursor = self.connection.cursor()
                col_data = self.query_data(sql_script)
                self.graph_data(col_data)
                # self.linear_regression(col_data)
        except (psycopg2.Error, FileNotFoundError) as e:
            print(f"An error occurred during database connection: {e}")
            raise SystemExit

    def query_data(self, sql_script):
        columns = self.get_columns(sql_script.arg1)
        execute_ = sql_script.arg1
        self.cursor.execute(execute_)
        data = self.cursor.fetchall()
        col_data = Args(arg1=columns, arg2=data)
        return col_data

    def graph_data(self, col_data):
        df = pd.DataFrame(col_data.arg2, columns=col_data.arg1)
        print(df)

    def linear_regression(self, data):
        pass
    
    @staticmethod
    def get_columns(sql):
        return list(i for i in map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql)) if not i.endswith('id'))

    def __del__(self):
        if self.cursor:
            self.cursor.close()


def main():
    sql_script = SQLFetch(open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[-1])
    db = DBConnect()
    db.sql_connect(sql_script)


if __name__ == '__main__':
    main()