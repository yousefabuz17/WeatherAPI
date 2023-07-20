import re
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import psycopg

from weather_data import WeatherForecast


class SQLParams(NamedTuple):
    host: str
    database: str
    user: str
    password: str


class SQLFetch(NamedTuple):
    arg1: str = None
    arg2: str = None
    arg3: str = None
    arg4: str = None


@dataclass(order=True)
class Args:
    arg1: str = None
    arg2: str = None
    
    # **Prints full database into a DataFrame
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

        data['timestamp'] = f"{data['location_name']} {data['day']} {data['hour']}"
        other_data['timestamp'] = f"{other_data['location_name']} other_data['day'] {other_data['hour']}"
        
        merged_data = pd.merge(data, other_data, on=on_, how=how_)
        merged_data.drop(columns=on_, inplace=True)

        for col in self.arg2:
            x_col = f"{col}_x"
            y_col = f"{col}_y"
            if x_col in merged_data.columns and y_col in merged_data.columns:
                merged_data[col] = merged_data.apply(lambda row: row[y_col] if pd.notna(row[y_col]) else row[x_col], axis=1)
                merged_data.drop(columns=[x_col, y_col], inplace=True)
        return GroupBy._reset(merged_data)
    
    def __getitem__(self, item):
        df = pd.DataFrame(self.arg1, columns=self.arg2)
        return df[item], GroupBy._reset(df)


class DBConnect:
    '''Returns full database and is printed in a pandas DataFrame structure \n
        ``'DBConnect(sql_script)'`` = /path/to/sql_script 
        ``'DBConnect()._.arg1'`` = All rows in the database server\n
        ``'DBConnect()._.arg2'`` = All columns
    '''
    sql_script = None
    
    def __init__(self, sql_script_path: str = None):
        self.sql_script = self.insert_sql(sql_script_path) or self.get_sql_script()
        self.connection = None
        self.cursor = None
        self.database = None
        self.validator()

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
        except (RecursionError, AttributeError) as e:
            return self._string(e)
    
    def __getattr__(self, _) -> str:
        try:
            if self.database is not None and hasattr(config, 'database'):
                return self.database
        except (RecursionError, NameError, AttributeError) as e:
            return self._string(e)
    
    def __str__(self):
        df = pd.DataFrame(self._.arg1, columns=self._.arg2)
        return df.__repr__()
    
    def _string(self, e=None) -> str:
        return f"Ensure 'config.json' file was entered correctly and the database is up and running. {e}"
    
    @staticmethod
    def insert_sql(sql_script_path: str = None) -> str:
        if sql_script_path:
            try:
                sql_script = open(sql_script_path).read().split('\n\n')
                return sql_script
            except (FileNotFoundError, AttributeError):
                return ''
        return ''
    @staticmethod
    def get_columns(sql: str) -> list:
        try:
            # **Fetching columns based on script rather than hard coding for practice
            return list(filter(lambda i: not i.endswith('id') and 's' not in i, map(lambda i: i.replace('.',''), re.findall(r'\.\w+', sql))))
        except TypeError:
            return 'Error encountered retrieving columns'
    
    @staticmethod
    def group_where(column: str) -> str:
        #! Add more if needed
        match column:
            case 'location_id':
                return 'WHERE l.location_id = '
            case _:
                return ''

    def get_sql_script(self) -> SQLFetch:
        try:
            sql_script = SQLFetch(open(Path(__file__).parent.absolute() / 'weather_db.sql').read().split('\n\n')[-1])
            return sql_script
        except FileNotFoundError:
            return 'Ensure that the SQL script (.sql) is located in the same folder as this program.'

    def validator(self):
        try:
            self.sql_connect()
        except AttributeError as e:
            return f'An error occurred during database connection: {e}'
    
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
            self._string(e)

    def query_data(self) -> Args:
        columns = self.get_columns(self.sql_script.arg1)
        execute_ = self.sql_script.arg1
        self.cursor.execute(execute_)
        rows = self.cursor.fetchall()
        col_data = Args(arg1=rows, arg2=columns)
        return col_data #**Returns the full database including columns
    
    def get_locations(self):
        try:
            self.cursor.execute('SELECT location_id, location_name FROM locations')
            results = self.cursor.fetchall()
            return results
        except (psycopg.errors.InvalidTextRepresentation, AttributeError) as e:
            return self._string(e)
    
    def group_location_id(self, column: str, value: str) -> Args:
        try:
            columns = self.get_columns(self.sql_script.arg1)
            sql_script = f'{self.sql_script.arg1[:-1]}\n{DBConnect.group_where(column)}\'{value}\';'
            self.cursor.execute(sql_script)
            rows = self.cursor.fetchall()
            data = Args(arg1=rows, arg2=columns)
            return data
        except (psycopg.errors.InvalidTextRepresentation, AttributeError) as e:
            return ValueError("Invalid input")


class GroupBy:
    database = Args(arg1=DBConnect()._.arg1, arg2=DBConnect()._.arg2)
    
    @staticmethod
    def _reset(pd_: pd.DataFrame | pd.Series | Args) -> Args | pd.Series:
        if isinstance(pd_, pd.DataFrame):
            rows = pd_.values.tolist()
            columns = pd_.columns.tolist()
            data_reset = Args(arg1=rows, arg2=columns)
            return data_reset
        
        elif isinstance(pd_, pd.Series):
            *data_reset, = pd_.tolist()
            return data_reset
        
        elif isinstance(pd_, Args):
            rows = pd_.arg1
            columns = pd_.arg2
            data_reset = Args(arg1=rows, arg2=columns)
            return data_reset
    
    @staticmethod
    def location_id(id_: int|str=None) -> Args:
        try:
            if id_ is not None:
                data = DBConnect().group_location_id('location_id', id_)
                return data
            return DBConnect().get_locations()
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return ValueError("Invalid input")
    
    @classmethod
    def filter_by_day(cls, day:str, data=None) -> Args:
        try:
            if data is None:
                data = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
            else:
                data = pd.DataFrame(data.arg1, columns=data.arg2)
            
            filtered_data = data[data['day'] == day]
            return GroupBy._reset(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return ValueError("Invalid input")
    
    @classmethod
    def filter_by_hour(cls, min_hour:int, max_hour:int, data=None) -> Args:
        min_hour, max_hour = map(lambda i: f'{str(i).zfill(2)}:00:00', [min_hour, max_hour])
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
            df['hour'] = df['hour'].astype(str)
            filtered_data = df[(df['hour'] >= min_hour) & (df['hour'] <= max_hour)]
            return GroupBy._reset(filtered_data)
            
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return ValueError("Invalid input")
    
    @classmethod
    def filter_by_condition(cls, condition, data=None) -> Args:
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
            filtered_data = df[df['condition'] == condition]
            return GroupBy._reset(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return ValueError("Invalid input")
    
    @classmethod
    def filter_by_temperature(cls, min_temp, max_temp, data=None) -> Args:
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
            filtered_data = df[(df['temp_fah'] >= min_temp) & (df['temp_fah'] <= max_temp)]
            return GroupBy._reset(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return ValueError("Invalid input")
    
    @classmethod
    def filter_by_humidity(cls, min_humidity, max_humidity, data=None) -> Args:
        try:
            if data is None:
                df = pd.DataFrame(cls.database.arg1, columns=cls.database.arg2)
            else:
                df = pd.DataFrame(data.arg1, columns=data.arg2)
            filtered_data = df[(df['humidity'] >= min_humidity) & (df['humidity'] <= max_humidity)]
            return GroupBy._reset(filtered_data)
        
        except (psycopg.errors.InvalidTextRepresentation, psycopg.errors.SyntaxError):
            return 'Invalid input' 

def main():
    try:
        sql_script_path = 'path/to/your/sql_script.sql'  # Specify the SQL script path here
        database = DBConnect(sql_script_path)
        db = Args(arg1=database._.arg1, arg2=database._.arg2)
        groupby = GroupBy()
        reset = groupby._reset
        loc = groupby.location_id
        cond = groupby.filter_by_condition
        temper = groupby.filter_by_temperature
        hum = groupby.filter_by_humidity
        day_ = groupby.filter_by_day
        hour_ = groupby.filter_by_hour
    except AttributeError:
        print(f'Ensure config.json file is configured properly and the SQL script (.sql) is located in the same folder as this program.')
    
if __name__ != '__main__':
    DBConnect
    GroupBy

main()
