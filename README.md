# Weather Forecast Application
This is a Python application that fetches and displays weather information using various APIs. It provides current weather data as well as a forecast for the upcoming days. The application allows users to specify a location or use the current location based on the IP address.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Examples](#examples)
    - [Simple Weather](#simple-weather)
    - [Weather Forecast](#weather-forecast)
- [Time Complexity Analysis](#time-complexity-analysis)
    - [Fetching Current Weather Data (Simple Weather)](#fetching-current-weather-data-simple-weather)
    - [Fetching Weather Forecast Data (Weather Forecast)](#fetching-weather-forecast-data-weather-forecast)
    - [Database Operations](#database-operations)
- [Progress](#progress)
- [Regression Modeling](#regression-modeling)
- [Future Enhancements](#future-enhancements)



## Introduction
The Weather Forecast Application is a Python application that fetches weather data and provides accurate weather information for any location. It utilizes various APIs and modules to retrieve weather data and present it to the user. The key APIs and modules used in this application are:

- requests: A Python library for making HTTP requests to fetch data from APIs.
- socket: A module that provides access to various networking functionalities, used to retrieve the IP address.
- geocoder: A Python library that provides geocoding capabilities, used to get the current location based on IP address.
- config.json: A module containing API keys for accessing weather APIs.
- emojis: A module that maps weather conditions to emojis for visual representation.



## Features

- Simple Weather: This class fetches and displays the current weather information. It uses the Weather API from weatherapi.com to retrieve data such as temperature, wind conditions, and humidity. (A simple class to display current weather depending on input)
    - [Time Complexity Analysis](#time-complexity-analysis)
- WeatherForecast: This class extends the Simple Weather class. It utilizes the Visual Crossing Weather API to fetch a detailed forecast for a specified location. The Weather Forecast functionality retrieves and stores hourly weather data for up to 15 days, including temperature, humidity, and weather conditions into a Postgresql database.
    - [Time Complexity Analysis](#time-complexity-analysis)
## Examples
### Simple Weather
![Screen Shot 2023-07-13 at 3 42 09 PM](https://github.com/yousefabuz17/FileCraftsman/assets/68834704/0982b1ca-bc32-4494-a6a8-18cf674c2319)
---
### Weather Forecast
- Weather forecast for up to 15 days ahead (Hourly)
- API data cleaned and formatted for better visualization
- GUI for better visiuallization and user experience
- Demo of the GUI coming soon
- [Regression Modeling](#regression-modeling)
- **Dashboard still in-development**
---
## Time Complexity Analysis
### ```Fetching Current Weather Data (Simple Weather)```:
The code for fetching current weather data has a time complexity of O(1). This is because it directly makes an HTTP request to the weather API and retrieves the required information. The time it takes to fetch the data remains constant, regardless of the size of the input or the number of iterations.

### ```Fetching Weather Forecast Data (Weather Forecast)```:
The code for fetching weather forecast data has a time complexity of O(1) as well. Similar to the simple weather functionality, it makes an HTTP request to the forecast API and retrieves the forecast data in a constant amount of time.

### ```Database Operations```:
The code for updating the SQL database with weather data has a time complexity of O(1) for each entry. The database operations, such as inserting location data, temperature data, and hourly data, are performed individually and do not depend on the size of the input or the number of existing entries.

## Database Tables

**Table: Locations**

| location_id | location_name         | longitude | latitude |
|-------------|-----------------------|-----------|----------|
| 1           | New York, NY, USA     | -74.0071  | 40.7146  |

**Table: Temperature**

| temperature_id | location_id | date       | min_temp_cel | min_temp_fah | max_temp_cel | max_temp_fah |
|----------------|-------------|------------|--------------|--------------|--------------|--------------|
| 1              | 1           | 2023-07-15 | 22.3         | 72.14        | 31.6         | 88.88        |
| 2              | 1           | 2023-07-16 | 22.3         | 72.14        | 31.6         | 88.88        |

**Table: Hourly**

| hourly_id | temperature_id | hour      | temp_cel | temp_fah | humidity | conditions |
|-----------|----------------|-----------|----------|----------|----------|------------|
| 1         | 1              | 00:00:00  | 22.8     | 73.04    | 88       | Rain       |
| 2         | 1              | 01:00:00  | ...      | ...      | ...      | ...        |
| ...       | ...            | ...       | ...      | ...      | ...      | ...        |
| 25        | 1              | 23:00:00  | ...      | ...      | ...      | ...        |
| 26        | 2              | 00:00:00  | 25.6     | 78.08    | ...      | ...        |
| 27        | 2              | 01:00:00  | ...      | ...      | ...      | ...        |
| ...       | ...            | ...       | ...      | ...      | ...      | ...        |
| 48        | 2              | 23:00:00  | ...      | ...      | ...      | ...        |

**Note: The ellipsis (...) represents the remaining rows of hourly data for each day.*

In this database structure, we have three tables: `Locations`, `Temperature`, and `Hourly`. The `Locations` table stores the location information, the `Temperature` table stores the temperature data for each day, and the `Hourly` table stores the hourly data for each day.

The tables are related using foreign key constraints. The `temperature_id` column in the `Hourly` table references the `temperature_id` column in the `Temperature` table, and the `location_id` column in the `Temperature` table references the `location_id` column in the `Locations` table.

## Progress
- [x] Simple Weather
- [x] Weather Forecast
- [ ] GUI/Dashboard
- [x] Automatic Location Detection
- [x] Real-Time Forecasts
- [ ] Predictive Model
    - [x] Regression
    - [ ] Historical Data for Predictive Modeling
- [x] SQL DB Integration
    - [x] Postgresql
    - [x] Updates DB each run with new data while storing old data for predicitve modeling
- [x] Exception Handling

## Regression Modeling
```
Results for New York, NY, United States:
        Temperature Regression Mean Squared Error: 1.686
        Temperature Regression R-squared: 0.938
        Weather Condition Classification Accuracy: 80.56%



Results for Fort Lauderdale, FL, United States:
        Temperature Regression Mean Squared Error: 0.497
        Temperature Regression R-squared: 0.966
        Weather Condition Classification Accuracy: 81.94%



Results for Beit Hanina Balad, HaGada HaMa'aravit:
        Temperature Regression Mean Squared Error: 1.898
        Temperature Regression R-squared: 0.966
        Weather Condition Classification Accuracy: 97.22%



Results for Barrio Patagonia, Bahía Blanca, Buenos Aires, Argentina:
        Temperature Regression Mean Squared Error: 1.223
        Temperature Regression R-squared: 0.957
        Weather Condition Classification Accuracy: 80.56%



Results for Desert, Green River, UT, United States:
        Temperature Regression Mean Squared Error: 1.625
        Temperature Regression R-squared: 0.979
        Weather Condition Classification Accuracy: 84.72%



Results for Antarctica:
        Temperature Regression Mean Squared Error: 4.522
        Temperature Regression R-squared: 0.933
        Weather Condition Classification Accuracy: 95.83%



Results for Tornado, WV, United States:
        Temperature Regression Mean Squared Error: 3.220
        Temperature Regression R-squared: 0.956
        Weather Condition Classification Accuracy: 79.17%



Results for Siberia, Matatiele, Eastern Cape, South Africa:
        Temperature Regression Mean Squared Error: 6.454
        Temperature Regression R-squared: 0.927
        Weather Condition Classification Accuracy: 86.11%



Results for Hayling Island, England, United Kingdom:
        Temperature Regression Mean Squared Error: 2.214
        Temperature Regression R-squared: 0.706
        Weather Condition Classification Accuracy: 80.56%



Results for Antarctica:
        Temperature Regression Mean Squared Error: 0.422
        Temperature Regression R-squared: 0.987
        Weather Condition Classification Accuracy: 95.83%
```

#### The weather forecast project yielded promising results, demonstrating the effectiveness of the predictive models in providing accurate temperature predictions and weather condition classifications for various locations.
    - The mean squared error (MSE) values were reasonably low, indicating minimal prediction errors in temperature forecasts.
    - The high R-squared (R2) values close to 1 suggested that the models effectively explained a significant portion of the temperature variability.
    - The weather condition classification accuracy also performed well, achieving approximately 80% or higher accuracy in most cases. These results affirm the reliability of the models in delivering reliable weather forecasts.




# Future Enhancements

- User-Friendly GUI: Transform the backend fetched data into a user-friendly GUI application, providing an intuitive and visually appealing interface for users to interact with the weather forecast.

- ~~Automatic Location Detection: Implement automatic location detection, where the application will detect the user's current location based on their IP address and display the weather forecast for the next 10+ days accordingly.~~

- Real-Time Forecasts: Allow users to input their desired location to view real-time weather forecasts. This feature will enable users to explore weather conditions and predictions for specific cities or regions.

- Predictive Model: Integrate a predictive model into the application to visually represent the potential weather outlook. By leveraging historical weather data and machine learning algorithms, the application can provide users with an estimated representation of future weather conditions.
