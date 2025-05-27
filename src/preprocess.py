from datetime import datetime, date
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
rain_1h = current_data.get('rain', {}).get('1h', 0)
snow_1h = current_data.get('snow', {}).get('1h', 0)

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
    "weather_icon": ", ".join(current_icons),
    "rain_1h_mm": rain_1h,
    "snow_1h_mm": snow_1h,  
}

with open('nagasaki_current.json', 'w') as f:
    json.dump(current_entry, f, indent=2)

# Get forecast data
forecast_response = requests.get(forecast_url)
forecast_data = forecast_response.json()

# Save only today's forecast as a separate JSON
today_str = date.today().strftime('%Y-%m-%d')
today_forecast = [
    {
        "time": entry['dt_txt'],
        "temp": entry['main']['temp'],
        "temp_max": entry['main']['temp_max'],
        "temp_min": entry['main']['temp_min'],
        "humidity": entry['main']['humidity'],
        "feels_like": entry['main']['feels_like'],
        "pressure": entry['main']['pressure'],
        "weather_main": ", ".join([w['main'] for w in entry.get('weather', [])]),
        "weather_description": ", ".join([w['description'] for w in entry.get('weather', [])]),
        "weather_icon": ", ".join([w['icon'] for w in entry.get('weather', [])]),
        "rain_mm": entry.get('rain', {}).get('3h', 0),
        "snow_mm": entry.get('snow', {}).get('3h', 0) 
    }
    for entry in forecast_data['list']
    if entry['dt_txt'].startswith(today_str)
]

with open('nagasaki_today_forecast.json', 'w') as f:
    json.dump(today_forecast, f, indent=2)

# Save 5-day temperature forecast as a new JSON
temps_5days = [
    {
        "time": entry['dt_txt'],
        "temp": entry['main']['temp'],
        "temp_max": entry['main']['temp_max'],
        "temp_min": entry['main']['temp_min'],
        "humidity": entry['main']['humidity'],
        "feels_like": entry['main']['feels_like'],
        "pressure": entry['main']['pressure'],
        "rain_mm": entry.get('rain', {}).get('3h', 0)
    }
    for entry in forecast_data['list']
]

with open('nagasaki_temps.json', 'w') as f:
    json.dump(temps_5days, f, indent=2)

# Typhoon prediction: collect entries with high wind and low pressure
typhoon_entries = []
for entry in forecast_data['list']:
    wind_speed = entry['wind']['speed']
    wind_gust = entry['wind'].get('gust', 0)
    pressure = entry['main']['pressure']
    if wind_speed >= 20 or pressure <= 990:
        typhoon_entries.append({
            "time": entry['dt_txt'],
            "wind_speed": wind_speed,
            "wind_gust": wind_gust,
            "pressure": pressure,
            "temp": entry['main']['temp'],
            "humidity": entry['main']['humidity'],
            "weather_main": ", ".join([w['main'] for w in entry.get('weather', [])]),
            "weather_description": ", ".join([w['description'] for w in entry.get('weather', [])]),
            "rain_mm": entry.get('rain', {}).get('3h', 0)
        })

with open('nagasaki_typhoon_predict.json', 'w') as f:
    json.dump(typhoon_entries, f, indent=2)




# ========================================================== #

# JMA Typhoon XML to JSON conversion live feed

# JMA_XML_URL = "https://www.data.jma.go.jp/developer/xml/feed/extra_typhoon.xml"
# JMA_XML_FILE = "jma_typhoon.xml"

# try:
#     # Download the XML
#     r = requests.get(JMA_XML_URL)
#     if r.status_code == 200:
#         with open(JMA_XML_FILE, "wb") as f:
#             f.write(r.content)
#         print("Downloaded JMA Typhoon XML.")

#         # Parse the XML
#         tree = ET.parse(JMA_XML_FILE)
#         root = tree.getroot()

#         # Example: Extract typhoon info from the feed
#         typhoons = []
#         for item in root.findall(".//item"):
#             typhoon = {
#                 "title": item.findtext("title"),
#                 "link": item.findtext("link"),
#                 "pubDate": item.findtext("pubDate"),
#                 "description": item.findtext("description"),
#             }
#             typhoons.append(typhoon)

#         # Save as JSON
#         with open("jma_typhoon_feed.json", "w") as f:
#             json.dump(typhoons, f, indent=2, ensure_ascii=False)
#         print("Saved JMA typhoon feed as jma_typhoon_feed.json.")
#     else:
#         print(f"Failed to download JMA XML: HTTP {r.status_code}")
# except Exception as e:
#     print(f"JMA Typhoon XML to JSON failed: {e}")

# ========================================================== #

# Fetch the live analysis EEW data from JMA earthquake data and convert to JSON
url = "https://api.wolfx.jp/jma_eew.json"
response = requests.get(url)
data = response.json()
# Fetch the latest earthquake list data from JMA and add to quake_info
eqlist_url = "https://api.wolfx.jp/jma_eqlist.json"
eqlist_response = requests.get(eqlist_url)
eqlist_data = eqlist_response.json()

fields = [
    "EventID", "Serial", "AnnouncedTime", "OriginTime", "Hypocenter",
    "Latitude", "Longitude", "Magunitude", "Depth", "MaxIntensity",
    "isSea", "isTraining", "isAssumption", "isWarn", "isFinal",
    "isCancel", "OriginalText", "Pond"
]

quake_info = {k: data.get(k) for k in fields}

# Extract and add specific subfields at the root level
accuracy = data.get("Accuracy", {})
quake_info["Epicenter"] = accuracy.get("Epicenter")
quake_info["DepthAccuracy"] = accuracy.get("Depth")
quake_info["MagnitudeAccuracy"] = accuracy.get("Magnitude")
maxintchange = data.get("MaxIntChange", {})
quake_info["String"] = maxintchange.get("String")
quake_info["Reason"] = maxintchange.get("Reason")
quake_info["WarnArea"] = data.get("WarnArea", [])

no_keys = [f"No{i}" for i in range(1, 11)]
quake_info["RecentList"] = {k: eqlist_data.get(k) for k in no_keys if k in eqlist_data}

with open("quake.json", "w", encoding="utf-8") as f:
    json.dump(quake_info, f, ensure_ascii=False, indent=2)