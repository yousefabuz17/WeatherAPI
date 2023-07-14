# Weather Forecast Application
This is a Python application that fetches and displays weather information using various APIs. It provides current weather data as well as a forecast for the upcoming days. The application allows users to specify a location or use the current location based on the IP address.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Examples](#examples)
- [Future Enhancements](#future-enhancements)



## Introduction
The Weather Forecast Application is convenient way to get accurate weather information for any location. It utilizes the following APIs and modules:

- requests: A Python library for making HTTP requests to fetch data from APIs.
- socket: A module that provides access to various networking functionalities, used to retrieve the IP address.
- geocoder: A Python library that provides geocoding capabilities, used to get the current location based on IP address.
- api_key: A module containing API keys for accessing weather APIs.
- emojis: A module that maps weather conditions to emojis for visual representation.



## Features

- Simple Weather: This class fetches and displays the current weather information. It uses the Weather API from weatherapi.com to retrieve data such as temperature, wind conditions, and humidity. (A simple class to display current weather depending on input)

- WeatherForecast: This class extends the SimpleWeather class and provides a forecast for the upcoming days. It utilizes the Visual Crossing Weather API to fetch a detailed forecast for a specified location.

## Examples
### Simple Weather
![Screen Shot 2023-07-13 at 3 42 09 PM](https://github.com/yousefabuz17/FileCraftsman/assets/68834704/0982b1ca-bc32-4494-a6a8-18cf674c2319)
---
### Weather Forecast
- Weather forecast for up to 15 days ahead (Hourly)
- GUI application for better visiuallization
- In-development

# Future Enhancements

- User-Friendly GUI: Transform the backend fetched data into a user-friendly GUI application, providing an intuitive and visually appealing interface for users to interact with the weather forecast.

- ~~Automatic Location Detection: Implement automatic location detection, where the application will detect the user's current location based on their IP address and display the weather forecast for the next 10+ days accordingly.~~

- Real-Time Forecasts: Allow users to input their desired location to view real-time weather forecasts. This feature will enable users to explore weather conditions and predictions for specific cities or regions.

- Predictive Model: Integrate a predictive model into the application to visually represent the potential weather outlook. By leveraging historical weather data and machine learning algorithms, the application can provide users with an estimated representation of future weather conditions.
