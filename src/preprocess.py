from datetime import datetime, date
import json
import requests

# -------------------- Ocean Monitoring Section --------------------

# List of ocean monitoring points (lat, lon)
OCEAN_POINTS = [
    # Pacific Ocean east of Japan
    (30.0, 145.0, "Pacific Ocean"),
    (35.0, 150.0, "Pacific Ocean"),
    (40.0, 155.0, "Pacific Ocean"),
    # Philippine Sea
    (20.0, 130.0, "Philippine Sea"),
    (25.0, 135.0, "Philippine Sea"),
    (15.0, 140.0, "Philippine Sea"),
    # South China Sea
    (18.0, 115.0, "South China Sea"),
    (22.0, 120.0, "South China Sea"),
    (15.0, 118.0, "South China Sea"),
]

# -------------------- Japan Bounding Box Section --------------------

# Japan bounding box (covers all main islands)
JAPAN_BBOX = {
    "min_lat": 24.396308,
    "max_lat": 45.551483,
    "min_lon": 122.93457,
    "max_lon": 153.986672
}

def is_in_japan(lat, lon):
    """Return True if the given lat/lon is within Japan's bounding box."""
    return (JAPAN_BBOX["min_lat"] <= lat <= JAPAN_BBOX["max_lat"] and
            JAPAN_BBOX["min_lon"] <= lon <= JAPAN_BBOX["max_lon"])
    
# -------------------- Weather Data Section --------------------

# API URLs
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?lat=35.4478&lon=139.6425&units=metric&appid=53d842d393e922cf8bddf6360e657e6a"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather?lat=35.4478&lon=139.6425&units=metric&appid=53d842d393e922cf8bddf6360e657e6a"

# Fetch current weather
current_response = requests.get(CURRENT_URL)
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

with open('current.json', 'w') as f:
    json.dump(current_entry, f, indent=2)

# Fetch forecast data
forecast_response = requests.get(FORECAST_URL)
forecast_data = forecast_response.json()

# Save only today's forecast
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

with open('today_forecast.json', 'w') as f:
    json.dump(today_forecast, f, indent=2)

# Save 5-day temperature forecast
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

with open('temps.json', 'w') as f:
    json.dump(temps_5days, f, indent=2)

# -------------------- Typhoon Prediction Section --------------------

API_KEY = "53d842d393e922cf8bddf6360e657e6a"
FORECAST_URL_TEMPLATE = "https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid=" + API_KEY

typhoon_entries_by_region = {
    "Pacific Ocean": [],
    "Philippine Sea": [],
    "South China Sea": []
}

for lat, lon, region in OCEAN_POINTS:
    url = FORECAST_URL_TEMPLATE.format(lat=lat, lon=lon)
    forecast_response = requests.get(url)
    forecast_data = forecast_response.json()
    for entry in forecast_data['list']:
        wind_speed = entry['wind']['speed']
        wind_gust = entry['wind'].get('gust', 0)
        pressure = entry['main']['pressure']
        if wind_speed >= 18 or pressure <= 995:
            typhoon_entry = {
                "time": entry['dt_txt'],
                "wind_speed": wind_speed,
                "wind_gust": wind_gust,
                "pressure": pressure,
                "lat": lat,
                "lon": lon,
                "region": region,
                "in_japan": is_in_japan(lat, lon),
                "temp": entry['main']['temp'],
                "humidity": entry['main']['humidity'],
                "weather_main": ", ".join([w['main'] for w in entry.get('weather', [])]),
                "weather_description": ", ".join([w['description'] for w in entry.get('weather', [])]),
                "rain_mm": entry.get('rain', {}).get('3h', 0)
            }
            typhoon_entries_by_region[region].append(typhoon_entry)

# Save each region's data to its own file
for region, entries in typhoon_entries_by_region.items():
    filename = f"typhoon_predict_{region.replace(' ', '_').lower()}.json"
    with open(filename, 'w') as f:
        json.dump(entries, f, indent=2)

# -------------------- Earthquake Data Section --------------------

# Fetch the live analysis EEW data from JMA earthquake data and convert to JSON
eew_url = "https://api.wolfx.jp/jma_eew.json"
eew_response = requests.get(eew_url)
eew_data = eew_response.json()

# Fetch the latest earthquake list data from JMA and add to quake_info
eqlist_url = "https://api.wolfx.jp/jma_eqlist.json"
eqlist_response = requests.get(eqlist_url)
eqlist_data = eqlist_response.json()

quake_fields = [
    "EventID", "Serial", "AnnouncedTime", "OriginTime", "Hypocenter",
    "Latitude", "Longitude", "Magunitude", "Depth", "MaxIntensity",
    "isSea", "isTraining", "isAssumption", "isWarn", "isFinal",
    "isCancel", "OriginalText", "Pond"
]

def fix_shindo(event):
    """Convert 'shindo' key to 'intensity' if present."""
    if isinstance(event, dict) and "shindo" in event:
        event["intensity"] = event.pop("shindo")
    return event

# Build quake_info dictionary
quake_info = {k: eew_data.get(k) for k in quake_fields}

# Extract and add specific subfields at the root level
accuracy = eew_data.get("Accuracy", {})
quake_info["Epicenter"] = accuracy.get("Epicenter")
quake_info["DepthAccuracy"] = accuracy.get("Depth")
quake_info["MagnitudeAccuracy"] = accuracy.get("Magnitude")
maxintchange = eew_data.get("MaxIntChange", {})
quake_info["String"] = maxintchange.get("String")
quake_info["Reason"] = maxintchange.get("Reason")
quake_info["WarnArea"] = eew_data.get("WarnArea", [])

# Get recent earthquake events
no_keys = [f"No{i}" for i in range(1, 11)]
quake_info["RecentList"] = {k: eqlist_data.get(k) for k in no_keys if k in eqlist_data}

# Fix shindo in RecentList for both quake.json and quake_points.json
for event in quake_info["RecentList"].values():
    fix_shindo(event)

# Save quake_info to quake.json
with open("quake.json", "w", encoding="utf-8") as f:
    json.dump(quake_info, f, ensure_ascii=False, indent=2)

# Prepare quake_points.json as an object with No as key and fixed events as value
quake_points = {
    no: fix_shindo(event.copy()) for no, event in quake_info["RecentList"].items()
}

# Convert quake_points from dict to array of objects with "No" field
quake_points_array = [
    {"No": no, **fix_shindo(event.copy())}
    for no, event in quake_info["RecentList"].items()
]

with open("quake_points.json", "w", encoding="utf-8") as f:
    json.dump(quake_points_array, f, ensure_ascii=False, indent=2)

# -------------------- Air Polution Data Section --------------------

def get_warning_level(value, good, moderate):
    if value <= good:
        return "Good"
    elif value <= moderate:
        return "Moderate"
    else:
        return "Unhealthy"

def air_quality_warnings(components):
    return [
        {
            "type": "co",
            "value": components["co"],
            "unit": "μg/m³",
            "level": get_warning_level(components["co"], 4400, 9400)
        },
        {
            "type": "pm2_5",
            "value": components["pm2_5"],
            "unit": "μg/m³",
            "level": get_warning_level(components["pm2_5"], 12, 35)
        },
        {
            "type": "pm10",
            "value": components["pm10"],
            "unit": "μg/m³",
            "level": get_warning_level(components["pm10"], 54, 154)
        }
    ]

# Fetch air pollution data
AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution?lat=35.4478&lon=139.6425&appid=53d842d393e922cf8bddf6360e657e6a"
air_response = requests.get(AIR_POLLUTION_URL)
air_data = air_response.json()

# Extract components and generate warnings
components = air_data["list"][0]["components"]
warnings = air_quality_warnings(components)

# Add warnings to the air_data dictionary
air_data["warnings"] = warnings

# Write the updated data back to air_pollution.json
with open('air_pollution.json', 'w') as f:
    json.dump(air_data, f, ensure_ascii=False, indent=2)