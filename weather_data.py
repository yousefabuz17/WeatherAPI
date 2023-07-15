import json
import os
import socket
import sys
from dataclasses import dataclass
from pathlib import Path

import geocoder
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from rapidfuzz import fuzz, process
from typing import NamedTuple
from base64 import b64encode, b64decode
from emojis import simple_weather_emojis as e

WIND_DIRECTIONS = {
    'N': 'North',
    'S': 'South',
    'E': 'East',
    'W': 'West',
    'NE': 'Northeast',
    'NW': 'Northwest',
    'SE': 'Southeast',
    'SW': 'Southwest',
    'NNE': 'North-northeast',
    'NNW': 'North-northwest',
    'ENE': 'East-northeast',
    'ESE': 'East-southeast',
    'SSE': 'South-southeast',
    'SSW': 'South-southwest',
    'WSW': 'West-southwest',
    'WNW': 'West-northwest',
}


class SimpleWeather: #! Turn into a simple GUI
    def __init__(self, place=None):
        self.place = place
        self.current_location = self.get_location()
        self.base_url = 'http://api.weatherapi.com/v1/current.json'
        self.query_params = {'key': WEATHER_API_KEY, 'q': self.place or self.get_location()}

    @staticmethod
    def get_ip_address():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
            return ip_address
        except socket.error as e:
            print("Error: Failed to fetch IP address.", e)
            raise SystemExit

    def get_location(self):
        try:
            ip_address = self.get_ip_address()
            response = requests.get('https://ipinfo.io/', params={
                'token': GEO_LOCATION,
                'ip': ip_address,
                'contentType': 'json'
            }).json()
            city = response.get('city')
            region = response.get('region')
            return city or region or 'Unknown'
        except requests.RequestException as e:
            print("Error: Failed to fetch location data.", e)
            raise SystemExit
        except geocoder.GeocoderTimedOut as e:
            print("Error: Geocoding timed out.", e)
            raise SystemExit

    def get_weather(self):
        try:
            response = requests.get(self.base_url, params=self.query_params)
            response.raise_for_status()
        except requests.RequestException as e:
            print("Error: Failed to fetch weather data.", e)
            raise SystemExit

        if response.status_code == 429:
            print("Error: Too many requests. Please try again later.")
            return self.get_weather()
        return response.json()

    def get_weather_data(self):
        data = self.get_weather()
        name = data['location']['name']
        unparsed_date = data['current']['last_updated'].split()[0].split('-')

        def parse_date(date_str: str):
            @dataclass
            class ParsedDate:
                year: str
                month: str
                day: str
            try: year, month, day = date_str.split('-')
            except (ValueError, AttributeError): year, month, day = '-'.join(date_str).split('-')
            
            return ParsedDate(year, month, day)

        date = parse_date(unparsed_date)
        condition = data['current']['condition']['text']
        f_degrees = data['current']['temp_f']
        feels_like = data['current']['feelslike_f']
        wind_mph = data['current']['wind_mph']
        wind_dir = data['current']['wind_dir']
        humidity = data['current']['humidity']
        get_weather_emoji = lambda condition: e.get(condition, '')

        return (
            name,
            date,
            condition,
            f_degrees,
            feels_like,
            wind_mph,
            wind_dir,
            humidity,
            get_weather_emoji(condition)
        )

    def display_weather_report(self):
        weather_data = self.get_weather_data()
        
        if not weather_data:
            print('No data for this location found.')
            return
        
        name, date, condition, f_degrees, feels_like, wind_mph, wind_dir, humidity, emoji = weather_data
        print(
            f'''\n \033[4;5;36;1mWeather Report for {name}\033[0m       \033[1;2m[Last Updated: {date.month}/{date.day}/{date.year}]\033[0m\n
            \033[1;31mTemperature:\033[0m {f_degrees}°F, but feels like {feels_like}°F
            \033[1;31mWind Speed:\033[0m {wind_mph} mph
            \033[1;31mWind Direction:\033[0m {wind_dir} ({WIND_DIRECTIONS.get(wind_dir, '')})
            \033[1;31mWeather Condition:\033[0m {condition} {emoji}
            \033[1;31mHumidity:\033[0m {humidity}%
            ''')
    
    @staticmethod
    def dump_json(data):
        forecast_json = Path(__file__).parent.absolute() / 'Forecast_data.json'
        if os.path.isfile(forecast_json) or not os.path.isfile(forecast_json):
            try:
                with open(forecast_json, 'w') as f:
                    json.dump(data, f, indent=2)
            except OSError as e:
                print("Error: Failed to write JSON data.", e)
                raise SystemExit


class WeatherForecast(SimpleWeather):
    def __init__(self, place=None):
        super().__init__(place)
        self.base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
        self.query_params = {
            'key': FORECAST_API_KEY,
            'contentType': 'json',
            'unitGroup': 'metric',
            'location': self.place or self.get_location(),
        }

    def get_weather(self):
        try:
            response = requests.get(self.base_url, params=self.query_params)
            response.raise_for_status()
            if response.status_code == 429:
                print("Error: Too many requests. Please try again later.")
                return None
            return response.json()
        except requests.RequestException as e:
            print("Error: Failed to fetch weather data.", e)
            raise SystemExit

    def full_weather_data(self):
        data = self.get_weather()
        if not data:
            data = []
        full_data = []
        
        class LocationInfo(NamedTuple):
            arg1: float
            arg2: float
        
        coordinates = LocationInfo(arg1=data['longitude'], arg2=data['latitude'])
        location_name = data['resolvedAddress']
        both_degrees = lambda c_temp: (c_temp, round((c_temp * 9 / 5) + 32, 2))  # (Celsius, Fahrenheit)
        
        min_temp = [both_degrees(data['days'][i]['tempmin']) for i in range(min(15, len(data['days'])))]
        min_temp = LocationInfo(arg1=min_temp[0], arg2=min_temp[1])
        
        max_temp = [both_degrees(data['days'][i]['tempmax']) for i in range(min(15, len(data['days'])))]
        max_temp = LocationInfo(arg1=max_temp[0], arg2=max_temp[1])
        
        for i in range(min(15, len(data['days']))):
            day_data = data['days'][i]
            day = day_data['datetime']
            hours = [day_data['hours'][idx]['datetime'] for idx in range(24)]
            humidity = [round(day_data['hours'][idx]['humidity']) for idx in range(24)]
            conditions = [[day_data['hours'][idx]['conditions'], ''] for idx in range(24)]
            hourly_temp = [both_degrees(day_data['hours'][idx]['temp']) for idx in range(24)]
            
            all_data = zip(hours, hourly_temp, humidity, conditions)
            day_full_data = list(all_data)
            full_data.append((location_name, coordinates, day, min_temp, max_temp, day_full_data))
        progress.update(25)
        return full_data

    def data_to_json(self, data=None):
        data = self.full_weather_data() if not data else data
        clean_data = []
        conditions = set()
        for _, element in enumerate(data):
            item = {
                'location': element[0],
                'coordinates': {'longitude': element[1].arg1,
                                'latitude': element[1].arg2},
                
                'day': element[2],
                'min_temp': {'Celcius':element[3].arg1,
                            'Fahrenheit':element[3].arg2},
                'max_temp': {'Celcius':element[4].arg1,
                            'Fahrenheit':element[4].arg2}
            }
            hourly_data = []
            for i in element[5]:
                conditions.add(i[3][0])
                hourly_item = {
                    'hour': i[0],
                    'temperature': {'Celcius': i[1][0],
                                    'Fahrenheit':i[1][1]},
                    'humidity': i[2],
                    'conditions': i[3][0],
                    'emoji': '' 
                }
                hourly_data.append(hourly_item)
            item['hourly_data'] = hourly_data
            clean_data.append(item)
        try:
            SimpleWeather.dump_json(clean_data)
        except OSError as e:
            print("Error: Failed to write JSON data.", e)
            raise SystemExit
        clean_data = WeatherIcons.modify_condition(clean_data)
        return clean_data


class WeatherConditons:
    def __init__(self):
        self.scrape_url = 'https://openweathermap.org/weather-conditions'

    def scrape_data(self):
        try:
            response = requests.get(self.scrape_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            tables = soup.find('table', class_='table')
            @dataclass
            class WeatherConditions:
                icon_code: str
                description: str

            data = []
            for icon_table in tables.find_all('tr'):
                cells = icon_table.find_all("td")
                if len(cells) >= 3:
                    for _, _ in enumerate(cells):
                        icon_code = cells[0].text.strip()[:3]
                        description = cells[-1].text.strip().title()
                    data.append(WeatherConditions(icon_code=icon_code, description=description))
            return data
        except requests.RequestException as e:
            print("Error: Failed to fetch weather conditions data.", e)
            raise SystemExit

class WeatherIcons:
    def __init__(self):
        self.base_url = 'https://openweathermap.org/img/wn/{}@2x.png'
    
    def parse_icon_url(self, icon_code):
        try:
            response = requests.get(self.base_url.format(icon_code))
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print("Error: Failed to fetch icon data.", e)
            raise SystemExit


    @staticmethod
    def modify_condition(data, condition=None):
        weather_conditions = WeatherConditons().scrape_data()
        unpacked = list(map(lambda i: [i.icon_code, i.description], weather_conditions))
        for item in data:
            hourly_data = item['hourly_data']
            for conditions in hourly_data:
                condition = conditions['conditions']
                emoji = conditions['emoji']
                best_match_ = process.extractOne(condition.lower(), list(map(lambda i: i.description, weather_conditions)), scorer=fuzz.ratio)
                best_match = best_match_[0] if best_match_ else ""
                conditions['conditions'] = best_match
                conditions['emoji'] = list(filter(lambda i: i[0] if i[1]==best_match else '', unpacked))[0][0] # [['03d', 'Scattered Clouds']] --> '03d' --> b'PNG' (after using modify_emoji)
        try:
            SimpleWeather.dump_json(data)
        except OSError as e:
            print("Error: Failed to write JSON data.", e)
            raise SystemExit
        WeatherIcons.modify_emoji()
        progress.update(25)
        return

    @staticmethod
    def modify_emoji():
        data = json.loads((Path(__file__).parent.absolute() / 'Forecast_data.json').read_text())
        weather_icons = WeatherIcons()
        codes = list({conditions['emoji'] for item in data for conditions in item['hourly_data']})
        
        for i in range(len(codes)):
            with open(Path.cwd() / 'icons' / f'{codes[i]}.png', 'wb') as file: #! To view png
                try:
                    png_bytes = weather_icons.parse_icon_url(codes[i])
                    file.write(png_bytes)
                    for item in data:
                        hourly_data = item['hourly_data']
                        for conditions in hourly_data:
                            conditions['emoji'] = {'Icon Code':codes[i],
                                                    'Bytes':b64encode(png_bytes).decode('utf-8')}
                            # encode back for bytes
                except OSError as e:
                    print("Error: Failed to write icon data.", e)
                    raise SystemExit
        progress.update(25)
        try:
            SimpleWeather.dump_json(data)
        except OSError as e:
            print("Error: Failed to write JSON data.", e)
            raise SystemExit
        return

#TODO: Add progress bar

def main():
    global WEATHER_API_KEY, GEO_LOCATION, FORECAST_API_KEY, progress
    config = json.load(open(Path(__file__).parent.absolute() / 'config.json', encoding='utf-8'))
    WEATHER_API_KEY = config['WEATHER_API_KEY']
    GEO_LOCATION = config['GEO_LOCATION']
    FORECAST_API_KEY = config['FORECAST_API_KEY']
    progress = tqdm(total=100, desc='\x1b[1;32mFetching forecast data\x1b\n[0m', ncols=80)
    try:
        simple_weather = input("\nWould you like a simple weather report? (y/n): ")
        place = input("Enter a location (leave empty for current location): ")
        if simple_weather == 'n':
            forecast = WeatherForecast(place)
            forecast.full_weather_data()
            forecast.data_to_json() # Full JSON forecast data
        else:
            SimpleWeather(place).display_weather_report()
    except KeyboardInterrupt:
        try:
            again = input("\nWould you like to try again?\nEnter a location (leave empty for current location):")
            WeatherForecast(again)
        except:
            print('\nProgram Terminated')
            sys.exit(0)
    except Exception as e:
        print("An unexpected error occurred.", e)
        sys.exit(1)

if __name__ == '__main__':
    main()

# TODO: Turn JSON into a well formatted SQL database
# - Database: WeatherForecastDB

#   - Collection: Locations
#     - Columns:
#       - location_id (unique identifier, e.g., ObjectId)
#       - location_name (string)
#       - coordinates (string)

#   - Collection: Forecasts
#     - Columns:
#       - forecast_id (unique identifier, e.g., ObjectId)
#       - location_id (reference to Locations collection)
#       - day (date)
#       - min_temp (array of tuples [(float, float)])
#       - max_temp (array of tuples [(float, float)])

#   - Collection: HourlyData
#     - Columns:
#       - hourly_id (unique identifier, e.g., ObjectId)
#       - forecast_id (reference to Forecasts collection)
#       - hour (string)
#       - temperature (tuple of floats)
#       - humidity (float)
#       - conditions (string)
#       - emoji (string or binary data for Base64 encoded PNG)


