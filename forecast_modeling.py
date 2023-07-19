import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import psycopg2
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

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
    ''''Returns full database in a DataFrame stucture \n
        'db.arg1' = All rows (Locations) in database server\n
        'db.arg2' = Columns'''
    def __init__(self):
        self.sql_script = DBConnect.get_sql_script()
        self.connection = None
        self.cursor = None
        self.database = None
        self.validator()
    
    def __str__(self): #**Prints full database into a DataFrame
        try:
            rows = self.database.arg1
            columns = self.database.arg2
            df = pd.DataFrame(rows, columns=columns)
            pd.set_option('display.max_columns', None)
            return df.__repr__() # For demonstration purposes
        except (AttributeError, FileNotFoundError) as e: 
            return self.__string(e)
    
    def __repr__(self):
        return self.__str__()

    def __del__(self):
        if self.cursor:
            self.cursor.close()
    
    def __getattr__(self, _):
        try:
            if self.database is not None and hasattr(config, 'database'):
                return self.database
            return AttributeError(self.__string())
        except (RecursionError, NameError) as e:
            return self.__string(e)
    
    def __string(self, e=None):
        return f"Ensure 'config.json' file was entered correctly and database is up and running. {e}"
    
    @staticmethod
    def get_columns(sql):
        try:
        #**Fetching columns based on script rather hard coding for practice
            return filter(lambda i: not i.endswith('id') and 's' not in i, map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql)))
        except TypeError:
            return f'Error encountered'
        
    @staticmethod
    def get_sql_script():
        try:
            sql_script = SQLFetch(open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[-1])
            return sql_script
        except FileNotFoundError:
            return f'Ensure that the SQL script (.sql) is located in the same folder as this program.'

    def validator(self):
        try: self.sql_connect()
        except AttributeError as e: return f'An error occurred during database connection: {e}'
    
    def sql_connect(self):
        global config
        config = SQLParams(*list(WeatherForecast.get_config().values())[-4:])
        try:
            with psycopg2.connect(
                                host=config.host,
                                database=config.database,
                                user=config.user,
                                password=config.password
                                ) as self.connection:
                self.cursor = self.connection.cursor()
                self.database = self.query_data()   #Args(arg1=Data, arg2= Columns)
        except (psycopg2.Error, psycopg2.OperationalError, FileNotFoundError, AttributeError) as e:
            self.__string(e)

    def query_data(self):
        columns = self.get_columns(self.sql_script.arg1)
        execute_ = self.sql_script.arg1
        self.cursor.execute(execute_)
        rows = self.cursor.fetchall()
        col_data = Args(arg1=rows, arg2=columns)
        return col_data #**Returns full database including columns
    
    def group_by_location(self, id_=None): #? Predictive testing for each location
        '''id_ (int): Location ID on Database Table'''
        try:
            columns = self.get_columns(self.sql_script.arg1)
            sql_script = f'{self.sql_script.arg1[:-1]}\nWHERE l.location_id = \'{id_}\''
            self.cursor.execute(sql_script)
            rows = self.cursor.fetchall()
            data = Args(arg1=rows, arg2=columns)
            return data
        except (psycopg2.errors.InvalidTextRepresentation, ValueError, AttributeError):
            return 'Invalid Location ID'


class GroupByLocation:
    db = None
    
    @classmethod
    def location_id(cls, id_=None):
        GroupByLocation.db = DBConnect()
        return GroupByLocation.db.group_by_location(id_)
    
    @classmethod
    def reset(cls, _):
        return GroupByLocation.db



def main():
    db = DBConnect()
    loc_group = GroupByLocation.location_id
    reset = GroupByLocation.reset
    print(db)

if __name__ == '__main__':
    main()
