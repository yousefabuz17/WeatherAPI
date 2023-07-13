import os
import json
import socket
import requests
import geocoder

from api_key import *
from functools import reduce
from pathlib import Path
from subprocess import call
from typing import NamedTuple
from bs4 import BeautifulSoup
from emojis import simple_weather_emojis as e

from api_key import WEATHER_API_KEY, FORECAST_API_KEY

WIND_DIRECTIONS = {
    'N': 'North',
    'S': 'South',
    'E': 'East',
    'W': 'West',
    'NE': 'Northeast',
    'NW': 'Northwest',
    'SE': 'Southeast',
    'SW': 'Southwest'
}


class Weather:
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
        except:
            return geocoder.ip('me').state

    def get_weather(self):
        try:
            response = requests.get(self.base_url, params=self.query_params)
        except requests.exceptions.RequestException:
            print("Error: Failed to fetch weather data.")
            raise SystemExit

        if response.status_code == 429:
            print("Error: Too many requests. Please try again later.")
            return self.get_weather()
        return response.json()

    def get_weather_data(self):
        data = self.get_weather()
        name = data['location']['name']
        unparsed_date = data['current']['last_updated'].split()[0].split('-')

        def parse_date(date_str: str) -> NamedTuple:
            class ParsedDate(NamedTuple):
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
        name, date, condition, f_degrees, feels_like, wind_mph, wind_dir, humidity, emoji = self.get_weather_data()
        print(
            f'''\n \033[4;5;36;1mWeather Report for {name}\033[0m       \033[1;2m[Last Updated: {date.month}/{date.day}/{date.year}]\033[0m\n
            \033[1;31mTemperature:\033[0m {f_degrees}°F, but feels like {feels_like}°F
            \033[1;31mWind Speed:\033[0m {wind_mph} mph
            \033[1;31mWind Direction:\033[0m {WIND_DIRECTIONS.get(wind_dir, wind_dir)}
            \033[1;31mWeather Condition:\033[0m {condition} {emoji}
            \033[1;31mHumidity:\033[0m {humidity}%
            ''')


class WeatherForecast(Weather):
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
            return response.json()
        except requests.exceptions.RequestException:
            print("Error: Failed to fetch weather data.")
            raise SystemExit

    def full_weather_data(self):
        data = self.get_weather()
        full_data = []
        long, lat = data['longitude'], data['latitude']
        location_name = data['resolvedAddress']
        both_degrees = lambda c_temp: (c_temp, round((c_temp * 9 / 5) + 32, 2))  # (Celsius, Fahrenheit)
        min_temp = [both_degrees(data['days'][i]['tempmin']) for i in range(min(15, len(data['days'])))]
        max_temp = [both_degrees(data['days'][i]['tempmax']) for i in range(min(15, len(data['days'])))]
        for i in range(min(15, len(data['days']))):
            day_data = data['days'][i]
            day = day_data['datetime']
            hours = [day_data['hours'][idx]['datetime'] for idx in range(24)]
            humidity = [round(day_data['hours'][idx]['humidity']) for idx in range(24)]
            conditions = [[day_data['hours'][idx]['conditions'], ''] for idx in range(24)]
            hourly_temp = [both_degrees(day_data['hours'][idx]['temp']) for idx in range(24)]
            all_data = zip(hours, hourly_temp, humidity, conditions)
            day_full_data = list(all_data)
            full_data.append((location_name, (long, lat), day, min_temp, max_temp, day_full_data))
        return self.data_to_json(full_data)

    def data_to_json(self, data):
        clean_data = []
        conditions = set()
        for _, element in enumerate(data):
            item = {
                'location': element[0],
                'coordinates': element[1],
                'day': element[2],
                'min_temp': element[3][_],
                'max_temp': element[4][_]
            }
            hourly_data = []
            for i in element[5]:
                conditions.add(i[3][0])
                hourly_item = {
                    'hour': i[0],
                    'temperature': i[1],
                    'humidity': i[2],
                    'conditions': i[3][0],
                    'emoji': ''  # Add emoji support later based on conditions
                }
                hourly_data.append(hourly_item)
            item['hourly_data'] = hourly_data
            clean_data.append(item)

        conditions = self.modify_conditions(conditions)
        if os.path.exists('WeatherAPI/') and not os.path.isfile('WeatherAPI/Forecast_data.json'):
            with open('WeatherAPI/Forecast_data.json', 'w') as f:
                json.dump(clean_data, f, indent=2)
        call(['/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code', 'WeatherAPI/Forecast_data.json'])
        return clean_data

    @staticmethod
    def modify_conditions(conditions):
        return WeatherIcons().modify_names(conditions)


class WeatherIcons:
    def __init__(self, content=None):
        self.base_url = 'https://openweathermap.org/img/wn/{}@2x.png'
        self.scrape_url = 'https://openweathermap.org/weather-conditions'

    def get_url(self):
        response = requests.get(self.base_url)
        return response

    def scrape_data(self):
        response = requests.get(self.scrape_url).text
        soup = BeautifulSoup(response, 'html.parser')
        tables = soup.find('table', class_='table')

        class WeatherConditions(NamedTuple):
            icon_code: str
            description: str

        data = []
        for icon_table in tables.find_all('tr'):
            cells = icon_table.find_all("td")
            if len(cells) >= 3:
                for idx, _ in enumerate(cells):
                    icon_code = cells[0].text.strip()[:3]
                    description = cells[-1].text.strip().title()
                data.append(WeatherConditions(icon_code=icon_code, description=description))
        return data

    def modify_names(self, conditions):
        print([i.split() for i in conditions])


if __name__ == '__main__':
    try:
        simple_weather = input("Would you like a simple weather report? (y/n): ")
        place = input("Enter a location (leave empty for current location): ")
        if simple_weather == 'n':
            weather_data = WeatherForecast(place).full_weather_data()
        else:
            Weather(place).display_weather_report()
    except KeyboardInterrupt:
        try:
            again = input("\nWould you like to try again?\nEnter a location (leave empty for current location):")
            weather_data = WeatherForecast(again).full_weather_data()
        except:
            quit()



    #openweatherapi api url, api key, and the contents (png file) off the url
    #base_url =  https://openweathermap.org/img/wn/
    #condition code = 10d@2x.png
    #base_url.content = png file for the emoji to be used in the GUI application
    #Retrieve the conditions from the cleaned JSON file from WeatherForecast class
    #Create a set to see all unique conditions
    #All conditions off API is under 'main' key
    #Create a method to retrieve the emoji based on the condition code
    #Then format the url to add the condition code to retrieve the png file
    #Class will be used to retrieve a list containing [condition, emoji]... Emoji is an empty string to be replaced
        #The argument being use for this class: i[3]
        #'conditions': i[3][0],
        #'emoji': i[3][1]
    #Not all conditions will have an emoji based on API being used
    #Filter conditions to be associated with an emoji no matter what
    #Replace the empty string with the emoji
    #Return the list of conditions with emojis to be used in the WeatherForecast class
    #Example of class being used:
    #Emoji().get_emoji(i[3])
        #'conditions': WeatherIcons(i[3]).get_emoji(), -> Output: 'conditions': 'Cloudy'
        #'emoji': WeatherIcons(i[3]).get_emoji()       -> Output: 'emoji': 'png file' (will be in bytes)
    #Complete