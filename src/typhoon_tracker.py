import os
import math
import json
import requests
import argparse
from datetime import datetime

# Small grid of ocean points (lat, lon, region)
OCEAN_POINTS = [
    (30.0, 145.0, "Pacific Ocean"),
    (35.0, 150.0, "Pacific Ocean"),
    (40.0, 155.0, "Pacific Ocean"),
    (20.0, 130.0, "Philippine Sea"),
    (25.0, 135.0, "Philippine Sea"),
    (15.0, 140.0, "Philippine Sea"),
    (18.0, 115.0, "South China Sea"),
    (22.0, 120.0, "South China Sea"),
    (15.0, 118.0, "South China Sea"),
]

API_KEY = os.environ.get("OPENWEATHER_API_KEY") or "53d842d393e922cf8bddf6360e657e6a"

def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two lat/lon points."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def fetch_forecast(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_current(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()

def build_forecast_track(grid_points, api_key):
    """Build a simple forecast track by choosing the grid point with lowest pressure per time step.

    This is a heuristic approach using OpenWeatherMap point forecasts sampled at a few ocean locations.
    """
    centers_by_dt = {}
    for lat, lon, region in grid_points:
        try:
            data = fetch_forecast(lat, lon, api_key)
        except Exception as e:
            print(f"Warning: forecast fetch failed for {lat},{lon}: {e}")
            continue
        for entry in data.get("list", []):
            dt = entry.get("dt_txt")
            if not dt:
                continue
            pressure = entry.get("main", {}).get("pressure")
            wind = entry.get("wind", {}).get("speed")
            prev = centers_by_dt.get(dt)
            better = False
            if prev is None:
                better = True
            else:
                prev_p = prev.get("pressure")
                prev_w = prev.get("wind")
                if pressure is not None and prev_p is not None:
                    if pressure < prev_p - 1e-6:
                        better = True
                    elif abs(pressure - prev_p) < 1e-6 and wind is not None and prev_w is not None and wind > prev_w:
                        better = True
                elif pressure is None and wind is not None and prev_w is not None and wind > prev_w:
                    better = True
            if better:
                centers_by_dt[dt] = {
                    "time": dt,
                    "lat": lat,
                    "lon": lon,
                    "region": region,
                    "pressure": pressure,
                    "wind": wind,
                }
    track = sorted(centers_by_dt.values(), key=lambda x: x["time"]) if centers_by_dt else []
    return track

def find_current_center(grid_points, api_key):
    best = None
    for lat, lon, region in grid_points:
        try:
            data = fetch_current(lat, lon, api_key)
        except Exception as e:
            print(f"Warning: current fetch failed for {lat},{lon}: {e}")
            continue
        pressure = data.get("main", {}).get("pressure")
        wind = data.get("wind", {}).get("speed")
        time = datetime.utcfromtimestamp(data.get("dt", 0)).isoformat() + "Z"
        if best is None:
            best = {"lat": lat, "lon": lon, "pressure": pressure, "wind": wind, "region": region, "time": time}
        else:
            prev_p = best.get("pressure")
            prev_w = best.get("wind")
            if pressure is not None and prev_p is not None:
                if pressure < prev_p - 1e-6:
                    best = {"lat": lat, "lon": lon, "pressure": pressure, "wind": wind, "region": region, "time": time}
                elif abs(pressure - prev_p) < 1e-6 and wind is not None and prev_w is not None and wind > prev_w:
                    best = {"lat": lat, "lon": lon, "pressure": pressure, "wind": wind, "region": region, "time": time}
            elif pressure is None and wind is not None and prev_w is not None and wind > prev_w:
                best = {"lat": lat, "lon": lon, "pressure": pressure, "wind": wind, "region": region, "time": time}
    return best

def predict_impacts(track, targets, radius_km=200.0):
    results = []
    for tlat, tlon, name in targets:
        min_dist = None
        min_time = None
        for p in track:
            d = haversine(tlat, tlon, p["lat"], p["lon"]) if isinstance(p, dict) else haversine(tlat, tlon, p[2], p[3])
            if min_dist is None or d < min_dist:
                min_dist = d
                min_time = p.get("time") if isinstance(p, dict) else None
        will_hit = (min_dist is not None and min_dist <= radius_km)
        results.append({
            "target_name": name or f"{tlat},{tlon}",
            "target_lat": tlat,
            "target_lon": tlon,
            "closest_distance_km": round(min_dist, 2) if min_dist is not None else None,
            "closest_time": min_time,
            "will_hit": will_hit,
            "threshold_km": radius_km,
        })
    return results

def parse_targets(strings):
    targets = []
    for s in strings:
        if ":" in s:
            coords, name = s.split(":", 1)
        else:
            coords, name = s, None
        lat_str, lon_str = coords.split(",")
        targets.append((float(lat_str.strip()), float(lon_str.strip()), name))
    return targets

def main():
    parser = argparse.ArgumentParser(description="Typhoon tracker and simple impact prediction using OpenWeatherMap forecasts.")
    parser.add_argument("--targets", "-t", nargs="+", help="Targets as lat,lon or lat,lon:Name (e.g. 35.68,139.69:Tokyo)")
    parser.add_argument("--radius", "-r", type=float, default=200.0, help="Impact radius in km (default 200)")
    parser.add_argument("--save", "-s", action="store_true", help="Save JSON outputs to typhoon_track.json")
    args = parser.parse_args()

    if not API_KEY:
        print("OpenWeather API key required. Set OPENWEATHER_API_KEY environment variable.")
        return

    grid = OCEAN_POINTS
    print("Building forecast track from sample ocean grid points...")
    track = build_forecast_track(grid, API_KEY)
    print(f"Forecast track points: {len(track)}")
    current = find_current_center(grid, API_KEY)

    if args.targets:
        targets = parse_targets(args.targets)
    else:
        targets = [(35.6895, 139.6917, "Tokyo"), (25.0330, 121.5654, "Taipei")]

    predictions = predict_impacts(track, targets, radius_km=args.radius)
    output = {"current_center": current, "forecast_track": track, "predictions": predictions}

    print(json.dumps(output, indent=2, ensure_ascii=False))

    if args.save:
        with open("typhoon_track.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
