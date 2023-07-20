import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd
import psycopg
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder

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


@dataclass(order=True)
class Args:
    arg1: str
    arg2: str
    
    #**Prints full database into a DataFrame
    def __str__(self):
        try:
            df = pd.DataFrame(self.arg1, columns=self.arg2)
            return str(df)
        except (AttributeError, TypeError):
            return
    
    def __add__(self, other, on_='timestamp', how_='outer'):
        if not isinstance(other, Args):
            raise ValueError("Can only add two Args instances.")
        
        data = pd.DataFrame(self.arg1, columns=self.arg2)
        other_data = pd.DataFrame(other.arg1, columns=other.arg2)
        
        data['hour'] = data['hour'].astype(str)
        other_data['hour'] = other_data['hour'].astype(str)

        data['timestamp'] = data['location_name'] + ' ' + data['day'] + ' ' + data['hour']
        other_data['timestamp'] = other_data['location_name'] + ' ' + other_data['day'] + ' ' + other_data['hour']
        
        merged_data = pd.merge(data, other_data, on=on_, how=how_)
        merged_data.drop(columns=on_, inplace=True)
        # merged_data = pd.concat([data, other_data], axis=0)
        # merged_data.drop(columns=on_, inplace=True)

        for col in self.arg2:
            x_col = f"{col}_x"
            y_col = f"{col}_y"
            if x_col in merged_data.columns and y_col in merged_data.columns:
                merged_data[col] = merged_data.apply(lambda row: row[y_col] if pd.notna(row[y_col]) else row[x_col], axis=1)
                merged_data.drop(columns=[x_col, y_col], inplace=True)
        return GroupBy.reset_pd_to_args(merged_data)
    
    def __getitem__(self, item):
        df = pd.DataFrame(self.arg1, columns=self.arg2)
        return df[item]



class DBConnect:
    ''''Returns full database in a DataFrame stucture \n
        'db._.arg1' = All rows (Locations) in database server\n
        'db._.arg2' = Columns
    '''
    def __init__(self):
        self.sql_script = DBConnect.get_sql_script()
        self.connection = None
        self.cursor = None
        self.database = None
        self.validator()

    def __del__(self):
        if self.cursor:
            self.cursor.close()
    
    def __getattr__(self, _) -> str:
        try:
            if self.database is not None and hasattr(config, 'database'):
                return self.database
            raise AttributeError(self.__string())   #!Remove later
        except (RecursionError, NameError) as e:
            return self.__string(e)
    
    def __str__(self):
        df = pd.DataFrame(self._.arg1, columns=self._.arg2)
        return df.__repr__()
    
    def __string(self, e=None) -> str:
        return f"Ensure 'config.json' file was entered correctly and database is up and running. {e}"
    
    @staticmethod
    def get_columns(sql: str) -> list:
        try:
        #**Fetching columns based on script rather hard coding for practice
            return list(filter(lambda i: not i.endswith('id') and 's' not in i, map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql))))
        except TypeError:
            return f'Error encountered'
    
    @staticmethod
    def group_where(column: str) -> str:
        #! Add more if needed
        match column:
            case 'location_id':
                return 'WHERE l.location_id = '
            case _:
                return ''
        

    @staticmethod
    def get_sql_script() -> SQLFetch:
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
            self.connection = psycopg.connect(
                host=config.host,
                dbname=config.database,
                user=config.user,
                password=config.password
            )
            self.cursor = self.connection.cursor()
            self.database = self.query_data()
        except (psycopg.Error, psycopg.OperationalError, FileNotFoundError, AttributeError) as e:
            self.__string(e)

    def query_data(self) -> Args:
        columns = self.get_columns(self.sql_script.arg1)
        execute_ = self.sql_script.arg1
        self.cursor.execute(execute_)
        rows = self.cursor.fetchall()
        col_data = Args(*[rows, columns])
        return col_data #**Returns full database including columns
    
    def group_locations(self, column: str, value: str) -> Args:
        try:
            columns = self.get_columns(self.sql_script.arg1)
            sql_script = f'{self.sql_script.arg1[:-1]}\n{DBConnect.group_where(column)}\'{value}\';'
            self.cursor.execute(sql_script)
            rows = self.cursor.fetchall()
            data = Args(*[rows, columns])
            return data
        except (psycopg.errors.InvalidTextRepresentation, ValueError, AttributeError) as e:
            raise e
            return 'Invalid Input'

#TODO: Make class to retrieve all values in specific columns

class GroupBy:
    database = Args(*[DBConnect()._.arg1, DBConnect()._.arg2])
    
    @staticmethod
    def reset_pd_to_args(pd_):
        rows = pd_.values.tolist()
        columns = pd_.columns.tolist()
        data_reset = Args(*[rows, columns])
        return data_reset
    
    @staticmethod
    def location_id(id_: int|str=None):
        try:
            data = DBConnect().group_locations('location_id', id_)
            return data
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input'
    
    @classmethod
    def filter_by_day(cls, day, data=None):
        try:
            if data is None:
                data = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
                filtered_data = data[data['day'] == day]
                return GroupBy.reset_pd_to_args(filtered_data)
            else:
                data = pd.DataFrame(data.arg1, columns=data.arg2)
                filtered_data = data[data['day'] == day]
                return GroupBy.reset_pd_to_args(filtered_data)
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input'
    
    @classmethod
    def filter_by_hour(cls, min_hour, max_hour, data=None):
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
                df['hour'] = pd.to_datetime(df['hour'])
                filtered_data = df[(df['min_hour'] >= min_hour) & (df['max_hour'] <= max_hour)]
                return GroupBy.reset_pd_to_args(filtered_data)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
                df['hour'] = pd.to_datetime(df['hour'])
                filtered_data = df[(df['min_hour'] >= min_hour) & (df['max_hour'] <= max_hour)]
                return GroupBy.reset_pd_to_args(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input' 
    
    @classmethod
    def filter_by_condition(cls, condition, data=None):
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
                filtered_data = df[df['condition'] == condition]
                return GroupBy.reset_pd_to_args(filtered_data)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
                filtered_data = df[df['condition'] == condition]
                return GroupBy.reset_pd_to_args(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input' 
    
    @classmethod
    def filter_by_temperature(cls, min_temp, max_temp, data=None):
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
                filtered_data = df[(df['temp_fah'] >= min_temp) & (df['temp_fah'] <= max_temp)]
                return GroupBy.reset_pd_to_args(filtered_data)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
                filtered_data = df[(df['temp_fah'] >= min_temp) & (df['temp_fah'] <= max_temp)]
                return GroupBy.reset_pd_to_args(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input'
    
    @classmethod
    def filter_by_humidity(cls, min_humidity, max_humidity, data=None):
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
                filtered_data = df[(df['humidity'] >= min_humidity) & (df['humidity'] <= max_humidity)]
                return GroupBy.reset_pd_to_args(filtered_data)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
                filtered_data = df[(df['humidity'] >= min_humidity) & (df['humidity'] <= max_humidity)]
                return GroupBy.reset_pd_to_args(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input' 

def main():
    database = DBConnect()
    db = Args(*[database._.arg1, database._.arg2])
    groupby = GroupBy()
    loc = groupby.location_id
    cond = groupby.filter_by_condition
    temper = groupby.filter_by_temperature
    hum = groupby.filter_by_humidity
    day_ = groupby.filter_by_day
    temp = loc(1)+loc(2)
    #!Make new file for sklearn
    # print(temp[temp['hour']>'00:00:00']) #Works
if __name__ == '__main__':
    main()
