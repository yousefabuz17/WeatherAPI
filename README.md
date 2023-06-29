# Weather Report Application
This is a Python application that fetches and displays weather information using various APIs. It provides current weather data as well as a forecast for the upcoming days. The application allows users to specify a location or use the current location based on the IP address.

## Introduction
The Weather Report Application is a simple and convenient way to get accurate weather information for any location. It utilizes the following APIs and modules:

-requests: A Python library for making HTTP requests to fetch data from APIs.

-socket: A module that provides access to various networking functionalities, used to retrieve the IP address.

-geocoder: A Python library that provides geocoding capabilities, used to get the current location based on IP address.

-api_key: A module containing API keys for accessing weather APIs.

-emojis: A module that maps weather conditions to emojis for visual representation.


## The application consists of two classes:

-Weather: This class fetches and displays the current weather information. It uses the Weather API from weatherapi.com to retrieve data such as temperature, wind conditions, and humidity. (A simple class to display current weather depending on input)

-WeatherForecast: This class extends the Weather class and provides a forecast for the upcoming days. It utilizes the Visual Crossing Weather API to fetch a detailed forecast for a specified location.
