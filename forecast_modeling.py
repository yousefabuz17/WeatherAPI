import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import numpy as np
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
    arg1: str=None
    arg2: str=None
    arg3: str=None
    arg4: str=None


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
            raise AttributeError(self.__string())
        except (RecursionError, NameError) as e:
            return self.__string(e)
    
    def __string(self, e=None):
        return f"Ensure 'config.json' file was entered correctly and database is up and running. {e}"
    
    @staticmethod
    def get_columns(sql):
        try:
        #**Fetching columns based on script rather hard coding for practice
            return list(filter(lambda i: not i.endswith('id') and 's' not in i, map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql))))
        except TypeError:
            return f'Error encountered'
    
    @staticmethod
    def group_where(column):
        match column:
            case 'location_id':
                return 'WHERE l.location_id = '
            case _:
                return ''
        

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
    
    def group_locations(self, column, value):
        try:
            columns = self.get_columns(self.sql_script.arg1)
            sql_script = f'{self.sql_script.arg1[:-1]}\n{DBConnect.group_where(column)}\'{value}\';'
            self.cursor.execute(sql_script)
            rows = self.cursor.fetchall()
            data = Args(arg1=rows, arg2=columns)
            return data
        except (psycopg2.errors.InvalidTextRepresentation, ValueError, AttributeError) as e:
            raise e
            return 'Invalid Input'



class GroupByLocation:
    database = DBConnect()

    @classmethod
    def location_id(cls, id_=None, db=None, viewtable=False):
        if db is None:
            db = cls.database
            data = cls.database.group_locations('location_id', id_)
            df = pd.DataFrame(data.arg1, columns=data.arg2)
            if bool(viewtable)==True:
                cls.__str__(df)
            return data
        else:
            if isinstance(db, DBConnect):
                df = pd.DataFrame(db._.arg1, columns=db._.arg2)
            else:
                df = pd.DataFrame(db.arg1, columns=db.arg2)
            if bool(viewtable)==True:
                cls.__str__(df)
            return db

    @classmethod
    def condition_type(cls, type_=None, db=None, viewtable=False):
        pass

    @classmethod
    def reset(cls, _):
        return cls.database
    
    @classmethod
    def __str__(cls, df):
        print(df)
        return df
        



def main():
    db = DBConnect()    #!'db._.arg1'
    grouper = GroupByLocation
    loc_group = grouper.location_id
    con_group = grouper.condition_type
    reset = grouper.reset
    d = loc_group(1)
    b = con_group('Shower Rain', d, viewtable=False)
    df = pd.DataFrame(d.arg1, columns=d.arg2)
    print(df.loc[df['condition'] == 'Broken Clouds', d.arg2])

    # first_table = loc_group(2)
    
    # second_table = con_group('Scattered Clouds', loc_group(1), viewtable=False)
    # df = pd.DataFrame(second_table.arg1, columns=second_table.arg2)
    # print(first_table)

if __name__ == '__main__':
    main()
