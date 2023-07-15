import json
import psycopg2

from dataclasses import dataclass
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
        print('hello')
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




