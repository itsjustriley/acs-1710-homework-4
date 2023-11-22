import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city');
    units = request.args.get('units');

    params = {
        "appid": API_KEY,
        "q": city,
        "units": units
    }

    result_json = requests.get(API_URL, params=params).json()

    date = datetime.now()
    sunrise = datetime.fromtimestamp(result_json['sys']['sunrise'])
    sunset = datetime.fromtimestamp(result_json['sys']['sunset'])
    formatted_date = date.strftime('%A %B %d, %Y')
    icon = result_json['weather'][0]['icon']
    icon_url = 'https://openweathermap.org/img/wn/' + icon + '.png'
    context = {
        'date': formatted_date,
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'degrees': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': sunrise.strftime('%H:%M'),
        'sunset': sunset.strftime('%H:%M'),
        'units': get_letter_for_units(units),
        'icon': icon_url
        
    }
    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!

    def get_weather(target_city):
        params = {
            "appid": API_KEY,
            "q": target_city,
            "units": units
        }
        date = datetime.now()
        result_json = requests.get(API_URL, params=params).json()
        sunrise = datetime.fromtimestamp(result_json['sys']['sunrise'])
        sunset = datetime.fromtimestamp(result_json['sys']['sunset'])
        icon = result_json['weather'][0]['icon']
        icon_url = 'https://openweathermap.org/img/wn/' + icon + '.png'
        new_context = {
            'date': date.strftime('%A %B %d, %Y'),
            'city': result_json['name'],
            'description': result_json['weather'][0]['description'],
            'degrees': result_json['main']['temp'],
            'humidity': result_json['main']['humidity'],
            'wind_speed': result_json['wind']['speed'],
            'sunrise': sunrise,
            'sunset': int(sunset.strftime('%H')),
            'units': get_letter_for_units(units),
            'icon': icon_url
        }
        return new_context

    city1_info = get_weather(city1)
    city2_info = get_weather(city2)

    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {
        'city1': city1_info,
        'city2': city2_info,

    }
    return render_template('comparison_results.html', **context)

@app.errorhandler(Exception)
def handle_error(error):
    return render_template('error.html'), 500


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
