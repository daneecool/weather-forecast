# File: /weather-grafana-preprocess/weather-grafana-preprocess/src/preprocess.py
import json
import requests

# URL of the JSON data
url = 'https://www.jma.go.jp/bosai/forecast/data/forecast/420000.json'

# Fetch the JSON from the URL
response = requests.get(url)
data = response.json()

# Get reportDatetime from the first object
report_datetime = data[0]['reportDatetime']

# Get "南部" and "北部" areas from the first timeSeries
areas = []
for area in data[0]['timeSeries'][0]['areas']:
    if area['area']['name'] in ['南部', '北部']:
        areas.append(area)

# Find the 長崎 temps block in the third timeSeries of the first object
nagasaki_temps = None
for area in data[0]['timeSeries'][2]['areas']:
    if area['area']['name'] == '長崎':
        nagasaki_temps = area
        break

# After finding nagasaki_temps
if nagasaki_temps and "temps" in nagasaki_temps:
    nagasaki_temps["temps"] = [int(x) for x in nagasaki_temps["temps"]]
    nagasaki_min = min(nagasaki_temps["temps"])
    nagasaki_max = max(nagasaki_temps["temps"])
else:
    nagasaki_min = None
    nagasaki_max = None

# Prepare nanbu and hokubu as empty dicts if not found
nanbu = areas[0] if len(areas) > 0 else {}
hokubu = areas[1] if len(areas) > 1 else {}

# Convert weatherCodes to integers if they exist
if nanbu and "weatherCodes" in nanbu:
    nanbu["weatherCodes"] = [int(x) for x in nanbu["weatherCodes"]]

# Combine into one flat result
result = {
    "reportDatetime": report_datetime,
    "nagasaki_min": nagasaki_min,
    "nagasaki_max": nagasaki_max,
    "nagasaki_lat": 32.7503,
    "nagasaki_lon": 129.8777,
    **({"nagasaki_" + k: v for k, v in nagasaki_temps.items()} if nagasaki_temps else {}),
    **({"nanbu_" + k: v for k, v in nanbu.items()} if nanbu else {}),
}

# Output the result as JSON
with open('nagasaki_temps.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('Saved to nagasaki_temps.json')