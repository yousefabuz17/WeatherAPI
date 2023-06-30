import json, socket, os.path, requests, geocoder
from api_key import *
from pathlib import Path
from subprocess import call
from typing import NamedTuple
from bs4 import BeautifulSoup
from emojis import simple_weather_emojis as e
from pprint import pprint

class Weather:
    def __init__(self, place=None):
        """
        Weather class to fetch and display current weather information.

        Args:
            place (str): Optional location to fetch weather information for.
        """
        self.place = place
        self.current_location = self.get_location()
        self.base_url = 'http://api.weatherapi.com/v1/current.json'
        self.query_params = {'key': WEATHER_API_KEY, 'q': self.place or self.get_location()}
        
    def get_ipaddress(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
            return ip_address
        except socket.error as e:
            print("Error: Failed to fetch IP address.", e)
            raise SystemExit
    
    def get_location(self):
        """
        Get the current location based on IP address using 2 different methods for retrieval if one fails.

        Returns:
            str: Current location.
        """
        try:
            ip_address = self.get_ipaddress()
            response = requests.get('https://ipinfo.io/',params={
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
        """
        Fetch weather information from the API.
        """
        try:
            response = requests.get(self.base_url, params=self.query_params)
        except requests.exceptions.RequestException: print("Error: Failed to fetch weather data."); raise SystemExit
        
        if response.status_code == 429:
                print("Error: Too many requests. Please try again later.")
                return self.get_weather()
        return response.json()
    
    def get_weather_data(self):
        """
        Display the weather report with relevant information.
        """
        data = self.get_weather()
        name = data['location']['name']
        unparsed_date = data['current']['last_updated'].split()[0].split('-')
        
        def parse_date(date_str: str) -> NamedTuple:
            """
            Parse the date string into year, month, and day.

            Args:
                date_str (str): Date string in the format 'YYYY-MM-DD'.

            Returns:
                NamedTuple: Parsed date information.
            """
            class ParsedDate(NamedTuple):
                year: str
                month: str
                day: str
            
            year, month, day = date_str
            
            return ParsedDate(year, month, day)
        
        date = parse_date(unparsed_date)
        condition = data['current']['condition']['text']
        f_degrees = data['current']['temp_f']
        feels_like = data['current']['feelslike_f']
        wind_mph = data['current']['wind_mph']
        wind_dir = data['current']['wind_dir']
        humidity = data['current']['humidity']
        get_weather_emoji = lambda condition: e.get(condition, '')
        
        return (name, date, condition, f_degrees, feels_like, wind_mph, wind_dir, humidity, get_weather_emoji(condition))
    
    def display_weather_report(self):
            """
            Display the weather report with relevant information.
            """
            name, date, condition, f_degrees, feels_like, wind_mph, wind_dir, humidity, emoji = self.get_weather_data()
            print(
            f'''\nWeather Report for {name}       [Last Updated: {date.month}/{date.day}/{date.year}]\n
            Temperature: {f_degrees}°F, but feels like {feels_like}°F
            Wind Conditions: {wind_mph} mph
            Wind Direction: {wind_dir}
            Weather Condition: {condition} {emoji}
            Humidity: {humidity}%
            ''')

class WeatherForecast(Weather):
    def __init__(self, place=None):
        super().__init__(place)
        self.base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'
        self.query_params = {'key': FORECAST_API_KEY,
                            'contentType': 'json',
                            'unitGroup': 'metric',
                            'location': self.place or self.get_location(),
                            }

    def get_weather(self):
        """
        Fetch weather information from the API.
        """
        try: response = requests.get(self.base_url, params=self.query_params); return response.json()
        except requests.exceptions.RequestException: print("Error: Failed to fetch weather data."); raise SystemExit
    
    def full_weather_data(self):
        """
        Fetches the full weather data including temperature range, hourly data, and other details for each day from 06/28/2023 - 07/12/2023.

        Returns:
        List[Tuple[str, float, float, List[Tuple[str, Tuple[float, float], int, str]]]]:
        Full weather data for each day.
            - Each tuple represents a day and contains the following information:
                - Day: The date of the weather data (YYYY-MM-DD).
                - Min_Temp/Max_temp: The min/max temperature in degrees (Celsius, Fahrenheit) for the day.
                - Hourly_Data: A list of tuples representing hourly weather data for the day.
                    - Each tuple contains the following information:
                        - Hour: The hour of the weather data (HH:00).
                        - Temperature: A list of tuples containing the current temperature in degrees (Celsius, Fahrenheit).
                        - Humidity: The humidity percentage.
                        - Conditions: The weather conditions.
                        - Emoji: The emoji associated with the weather conditions.
                        
        """
        data = self.get_weather()
        full_data = []
        long, lat = data['longitude'], data['latitude']
        location_name = data['resolvedAddress']
        both_degrees = lambda c_temp: (c_temp,round((c_temp * 9/5) + 32, 2))    #(Celsius, Fahrenheit)
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
            full_data.append((location_name, (long,lat), day, min_temp, max_temp, day_full_data))
        return self.data_to_json(full_data)
    
    def data_to_json(self, data):
        clean_data = []
        for _, element in enumerate(data):
            item = {
                'location': element[0],
                'coordinates': element[1], 
                'day': element[2],
                'min_temp': element[3][_],
                'max_temp': element[4][_]
            }
            hourly_data = []
            conditions = []
            for i in element[5]:
                conditions.append(i[3][0])
                hourly_item = {
                    'hour': i[0],
                    'temperature': i[1],
                    'humidity': i[2],
                    'conditions': i[3][0],  #Change to WeatherIcons(i[3][0]).get_emoji() later
                    'emoji': i[3][1]    #Add emoji support later based on conditions
                }
                hourly_data.append(hourly_item)
            item['hourly_data'] = hourly_data
            clean_data.append(item)
        
        conditions = self.modify_conditions(set(conditions))
        #Change this later for better detection for fun.
        #Add to detect what the users default text editor is and open the json file there.
        if os.path.exists('WeatherAPI/') and not os.path.isfile('WeatherAPI/Forecast_data.json'):
            with open('WeatherAPI/Forecast_data.json', 'w') as f:
                json.dump(clean_data, f, indent=2)
        # else:
        #     with open(f'{Path.home()}/Full_Data.json', 'w') as f:
        #         print(f'Writing to {Path.home()}/Full_Data.json instead.')
        #         json.dump(clean_data, f, indent=2)
        call(['/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code', 'WeatherAPI/Forecast_data.json'])
        return clean_data

    def modify_conditions(self, conditions):
        #Change wording of conditions to be more equivalent to the API description
        return WeatherIcons().modify_names(conditions)

class WeatherIcons:
    def __init__(self, content=None):
        self.base_url = 'https://openweathermap.org/img/wn/{}@2x.png' #To be formatted to obtain the png file
        # self.condition, self.emoji = condition[0], condition[1] #['Cloudy', '']
        self.scrape_url = 'https://openweathermap.org/weather-conditions' #To be scraped to obtain the charts
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
            if len(cells) >=3:
                for idx, _ in enumerate(cells):
                    icon_code = cells[0].text.strip()[:3]
                    description = cells[-1].text.strip().title()
                data.append(WeatherConditions(icon_code=icon_code, description=description))
        return data
    
    def modify_names(self, conditions):
        print(conditions)
    
    
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

if __name__ == '__main__':
    try:
        simple_weather = input("Would you like a simple weather report? (y/n): ")
        place = input("Enter a location (leave empty for current location): ")
        if simple_weather=='n':
            weather_data = WeatherForecast(place).full_weather_data()
        else:
            Weather(place).display_weather_report()
    except KeyboardInterrupt:
        try:
            again = input("\nWould you like to try again?\nEnter a location (leave empty for current location):")
            weather_data = WeatherForecast(again).full_weather_data()
        except: quit()
