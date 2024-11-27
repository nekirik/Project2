from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

API_KEY = os.getenv("ACCUWEATHER_TOKEN")


def get_weather(city):
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city}&language=ru-ru"
    location_data = requests.get(location_url).json()
    if location_data:
        location_key = location_data[0]['Key']
        weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru-ru&details=true"
        weather_data = requests.get(weather_url).json()
        if weather_data:
            return {
                "city": city,
                "temperature": weather_data[0]['Temperature']['Metric']['Value'],
                "humidity": weather_data[0]['RelativeHumidity'],
                "wind_speed": round(weather_data[0]['Wind']['Speed']['Metric']['Value']/3.6, 2),
                "precipitation": weather_data[0]['HasPrecipitation'],
                "weather_text": weather_data[0]['WeatherText']
            }
    return None


def check_bad_weather(weather, temperature, humidity, wind_speed):
    conditions = {}
    if temperature and float(temperature) + 5 >= weather['temperature'] >= float(temperature) - 5:
        conditions['temperature'] = 'Температура благоприятная(задана: вручную)'
    elif 35 >= weather['temperature'] >= 0:
        conditions['temperature'] = 'Температура благоприятная(задана: авто)'
    else:
        if wind_speed:
            conditions['temperature'] = 'Температура не благоприятная(задана: вручную)'
        else:
            conditions['temperature'] = 'Температура не благоприятная(задана: авто)'

    if humidity and float(humidity) + 10 >= weather['humidity'] >= float(humidity) - 10:
        conditions['humidity'] = 'Влажность благоприятная(задана: вручную)'
    elif 80 >= weather['humidity'] >= 60:
        conditions['humidity'] = 'Влажность благоприятная(задана: авто)'
    else:
        if humidity:
            conditions['humidity'] = 'Влажность не благоприятная(задана: вручную)'
        else:
            conditions['humidity'] = 'Влажность не благоприятная(задана: авто)'

    if wind_speed and float(wind_speed) >= weather['wind_speed']:
        conditions['wind_speed'] = 'Скорость ветра благоприятная(задана: вручную)'
    elif 15 >= weather['wind_speed']:
        conditions['wind_speed'] = 'Скорость ветра благоприятная(задана: авто)'
    else:
        if wind_speed:
            conditions['wind_speed'] = 'Скорость ветра не благоприятная(задана: вручную)'
        else:
            conditions['wind_speed'] = 'Скорость ветра не благоприятная(задана: авто)'
    return conditions


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form['start_city']
    end_city = request.form['end_city']

    preferenced_temperature = request.form['temperature']
    preferenced_humidity = request.form['humidity']
    preferenced_wind_speed = request.form['wind_speed']
    start_weather = get_weather(start_city)
    end_weather = get_weather(end_city)
    if not start_weather or not end_weather:
        return render_template('error.html', error_message='Один или два города не найдены(или API введено некорректно)')


    try:
        start_conditions = check_bad_weather(start_weather, preferenced_temperature, preferenced_humidity,
                                            preferenced_wind_speed)
        end_conditions = check_bad_weather(end_weather, preferenced_temperature, preferenced_humidity,
                                        preferenced_wind_speed)
    except:
        return render_template('error.html', error_message='Произошла ошибка при работе с API. Возможно был израсходован суточный лимит запросов.')

    return render_template('res.html', start_weather=start_weather, end_weather=end_weather,
                           start_conditions=start_conditions, end_conditions=end_conditions)


if __name__ == '__main__':
    app.run(debug=True)
