from datetime import datetime
import json
import requests

# Forecast data (metric)
forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat=32.7503&lon=129.8777&units=metric&appid=53d842d393e922cf8bddf6360e657e6a"
# Current weather data (metric)
current_url = "https://api.openweathermap.org/data/2.5/weather?lat=32.7503&lon=129.8777&units=metric&appid=53d842d393e922cf8bddf6360e657e6a"

# Get current weather
current_response = requests.get(current_url)
current_data = current_response.json()
current_mains = [w['main'] for w in current_data.get('weather', [])]
current_descriptions = [w['description'] for w in current_data.get('weather', [])]
current_icons = [w['icon'] for w in current_data.get('weather', [])]
current_time_str = datetime.utcfromtimestamp(current_data['dt']).strftime('%Y-%m-%d %H:%M:%S')
current_entry = {
    "time": current_time_str,
    "temp": current_data['main']['temp'],
    "temp_max": current_data['main']['temp_max'],
    "temp_min": current_data['main']['temp_min'],
    "humidity": current_data['main']['humidity'],
    "feels_like": current_data['main']['feels_like'],
    "pressure": current_data['main']['pressure'],
    "weather_main": ", ".join(current_mains),
    "weather_description": ", ".join(current_descriptions),
    "weather_icon": ", ".join(current_icons)
}

with open('nagasaki_current.json', 'w') as f:
    json.dump(current_entry, f, indent=2)

# Get forecast data
forecast_response = requests.get(forecast_url)
forecast_data = forecast_response.json()

result = []
for entry in forecast_data['list']:
    mains = [w['main'] for w in entry.get('weather', [])]
    descriptions = [w['description'] for w in entry.get('weather', [])]
    icons = [w['icon'] for w in entry.get('weather', [])]
    result.append({
        "time": entry['dt_txt'],
        "temp": entry['main']['temp'],
        "temp_max": entry['main']['temp_max'],
        "temp_min": entry['main']['temp_min'],
        "humidity": entry['main']['humidity'],
        "feels_like": entry['main']['feels_like'],
        "pressure": entry['main']['pressure'],
        "weather_main": ", ".join(mains),
        "weather_description": ", ".join(descriptions),
        "weather_icon": ", ".join(icons)
    })

with open('nagasaki_temps.json', 'w') as f:
    json.dump(result, f, indent=2)