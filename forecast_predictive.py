import warnings

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from groupby_db import DBConnect, GroupBy


class WeatherManager:
    def __init__(self, database):
        self.database = database
        self.get_tables()

    def fix_time(self, time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    def get_tables(self):
        num_locations = len(self.database.get_locations)
        for i in range(1, num_locations):
            df = pd.DataFrame(loc(i).arg1, columns=loc(i).arg2)
            self.regression_model(df)
    
    def regression_model(self, data):
        location = reset(data).arg1[0][0]
        data.columns = data.columns.str.strip()
        data['hour'] = data['hour'].apply(lambda t: t.strftime('%H:%M:%S'))
        data['hour'] = data['hour'].apply(lambda i: self.fix_time(i))
        data['day'] = pd.to_datetime(data['day'], format='%m/%d/%Y')
        data['day'] = data['day'].astype(int) / 10**9
        label_encoder = LabelEncoder()
        data['condition_encoded'] = label_encoder.fit_transform(data['condition'])

        temp_features = ['humidity', 'hour', 'day']
        temp_target = 'temp_fah'

        cond_features = ['humidity', 'hour', 'day']
        cond_target = 'condition_encoded'

        X_temp = data[temp_features]
        Y_temp = data[temp_target]

        X_cond = data[cond_features]
        Y_cond = data[cond_target]
        
        X_temp_train, X_temp_test, y_temp_train, y_temp_test = train_test_split(X_temp, Y_temp, test_size=0.2, random_state=42)
        X_cond_train, X_cond_test, y_cond_train, y_cond_test = train_test_split(X_cond, Y_cond, test_size=0.2, random_state=42)
        
        
        scaler = StandardScaler()
        X_temp_train_scaled = scaler.fit_transform(X_temp_train)
        X_temp_test_scaled = scaler.transform(X_temp_test)
        param_grid_regression = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10]
        }
        regression_model = RandomForestRegressor(random_state=42)
        grid_search_regression = GridSearchCV(regression_model, param_grid=param_grid_regression, cv=5, n_jobs=-1)
        grid_search_regression.fit(X_temp_train_scaled, y_temp_train)
        best_regression_model = grid_search_regression.best_estimator_

        y_temp_pred = best_regression_model.predict(X_temp_test_scaled)
        mse_temp = mean_squared_error(y_temp_test, y_temp_pred)

        param_grid_classification = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 5, 10, 15],
            'min_samples_split': [2, 5, 10]
        }
        classification_model = RandomForestClassifier(random_state=42)
        grid_search_classification = GridSearchCV(classification_model,param_grid=param_grid_classification, cv=5, n_jobs=-1)
        grid_search_classification.fit(X_cond_train, y_cond_train)
        best_classification_model = grid_search_classification.best_estimator_

        y_cond_pred = best_classification_model.predict(X_cond_test)
        accuracy_cond = accuracy_score(y_cond_test, y_cond_pred)
        accuracy_percentage = accuracy_cond * 100
        
        print(f'\nResults for {location}:')
        print(f'\tTemperature Regression Mean Squared Error: {mse_temp}')
        print(f'\tWeather Condition Classification Accuracy: {accuracy_percentage:.2f}%\n\n')

def main():
    global loc, reset
    groupby = GroupBy()
    reset = groupby._reset
    loc = groupby.location_id
    
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        WeatherManager(DBConnect())

if __name__ =='__main__':
    main()