import json
import psycopg2


from dataclasses import dataclass
from typing import NamedTuple
from pathlib import Path

class ForecastDB:
    def __init__(self, sql_params):
        self.data = ForecastDB.load_json('Forecast_data.json')
        self.config = sql_params
        self.sql_connect(self.config)
        
    
    @staticmethod
    def load_json(file):
        return json.load(open(Path(__file__).parent.absolute() / file, encoding='utf-8'))
    
    @staticmethod
    def config_user(self):
        config = ForecastDB.load_json('config.json')
        return self.sql_connect(config)
    
    def sql_connect(self, config_):
        global connection, cursor
        
        @dataclass
        class SqlParams:
            host: str
            database: str
            user: str
            password: str
        
        config = SqlParams(*config_)

        connection = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password
        )
        cursor = connection.cursor()
        self.update_db(self.data)
        
    def update_db(self, data):
        
        global LocationInfo
        class LocationInfo(NamedTuple):
            arg1: float
            arg2: float
        
        for day_data in data:
            location_name = day_data['location']
            coordinates = LocationInfo(arg1=day_data['coordinates']['longitude'],
                                        arg2='latitude')
            execute_first_query = 'INSERT INTO Locations (location_name, longitude, latitude, \
                            coordinate) VALUES (%s %s %s %s) RETURNING location_id'
            cursor.execute(execute_first_query, (location_name, coordinates.arg1, coordinates.arg2,
                                        psycopg2.extensions.AsIs(f"POINT({coordinates.arg1} {coordinates.arg2})")))
            locations_id = cursor.fetchone()[0]
            
            
            min_temp = LocationInfo(arg1=day_data['min_temp']['Celcius'],
                                    arg2=day_data['min_temp']['Fahrenheit'])
            max_temp = LocationInfo(arg1=day_data['max_temp']['Celcius'],
                                    arg2=day_data['max_temp']['Fahrenheit'])
            execute_second_query = 'INSERT INTO Temperature (location_id, )'
            
            forecast_id = cursor.fetchone()[0]
            
            for hourly in day_data['hourly_data']:
                hour = hourly['hour']
                hourly_temp = LocationInfo(arg1=hourly['temperature']['Celcius'],
                                            arg2=hourly['temperature']['Fahrenheit'])
                humidity = hourly['humidity']
                conditions = hourly['conditions']
                emoji = LocationInfo(arg1=hourly['emoji']['Icon Code'],
                                    arg2=hourly['emoji']['Decoded Bytes'])
                execute_second_query = 'INSERT INTO '
                
            
        
        
        return self.close_db()
    
    def close_db(self):
        connection.commit()
        cursor.close()
        connection.close()
        return
        

def main():
    config = ForecastDB.load_json('config.json')
    sql_params = list(map(lambda i: config.get(i, ''), config))[-4:]
    forecast_sql = ForecastDB(sql_params)


if __name__ == '__main__':
    main()




