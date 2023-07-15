import json
import psycopg2
from dataclasses import dataclass
from datetime import datetime as dt
from typing import NamedTuple
from datetime import datetime, timedelta
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
    def config_user():
        config = ForecastDB.load_json('config.json')
        return config

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
        self.create_tables()
        self.update_db(self.data)

    def create_tables(self):
        start_date = datetime.now().date()
        
        class ParsedDate(NamedTuple):
            year: int
            month: int
            day: int
        
        for day in range(15):
            date = ParsedDate(*list(map(lambda i: int(i), self.data[day]['date'].split('-'))))
            table_name = f"Day_{date.month}_{date.day}_{date.year}"
            self.create_day_table(table_name)
            for hour in range(24):
                hour_table_name = f"{table_name}_Hour_{hour:02d}"
                self.create_hour_table(hour_table_name)

    def create_day_table(self, table_name):
        
        class SqlInfo(NamedTuple):
            location: str
            temperature: str
            hourly: str
            weatheremoji: str
        
        weather_db = SqlInfo(*open(Path.cwd() / 'weather_db.sql').read().split('\n'))
        
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                       f"temperature_id SERIAL PRIMARY KEY,"
                       f"location_id INTEGER REFERENCES Locations(location_id),"
                       f"day DATE,"
                       f"min_temp_cel DECIMAL(4,2),"
                       f"min_temp_fah DECIMAL(4,2),"
                       f"max_temp_cel DECIMAL(4,2),"
                       f"max_temp_fah DECIMAL(4,2)"
                       f")")

    def create_hour_table(self, table_name):
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ("
                       f"hourly_id SERIAL PRIMARY KEY,"
                       f"temperature_id INTEGER REFERENCES Temperature(temperature_id),"
                       f"hour TIME,"
                       f"temp_cel DECIMAL(4,2),"
                       f"temp_fah DECIMAL(4,2),"
                       f"humidity INTEGER,"
                       f"conditions VARCHAR(255)"
                       f")")

    def update_db(self, data):
        pass
        # Update the database based on the data

    def close_db(self):
        connection.commit()
        cursor.close()
        connection.close()


def main():
    config = ForecastDB.load_json('config.json')
    sql_params = list(map(lambda i: config.get(i, ''), config))[-4:]
    forecast_sql = ForecastDB(sql_params)


if __name__ == '__main__':
    main()
