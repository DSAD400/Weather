#!/usr/bin/env python3
"""
Fetch hourly weather data using OpenWeatherMap API and export to Excel.
This is an alternative to scraping weather.com which has strong anti-bot protection.

To use this script:
1. Get a free API key from: https://openweathermap.org/api
2. Set the API_KEY variable below or pass it as an environment variable
"""

import os
import json
from datetime import datetime
from curl_cffi import requests
import pandas as pd


# OpenWeatherMap API configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")  # Get free key from openweathermap.org

# City coordinates (from earlier searches)
CITIES = {
    "La Grange, CA": {"lat": 37.6700, "lon": -120.6500},
    "Modesto, CA": {"lat": 37.6391, "lon": -121.0099},
    "Turlock, CA": {"lat": 37.4947, "lon": -120.8466}
}


def fetch_hourly_weather(city_name, lat, lon, api_key):
    """
    Fetch hourly weather forecast from OpenWeatherMap.

    Args:
        city_name: Name of the city
        lat: Latitude
        lon: Longitude
        api_key: OpenWeatherMap API key

    Returns:
        List of hourly weather data dictionaries
    """
    print(f"Fetching weather for {city_name}...")

    # OpenWeatherMap One Call API 3.0 endpoint (free tier)
    url = f"https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "imperial",  # Fahrenheit
        "exclude": "current,minutely,daily,alerts"
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 401:
            print(f"  ✗ Invalid API key. Get a free key from: https://openweathermap.org/api")
            return []

        if response.status_code != 200:
            print(f"  ✗ Error: Status {response.status_code}")
            # Try the older 2.5 API endpoint (free tier)
            url_v2 = "https://api.openweathermap.org/data/2.5/forecast"
            params_v2 = {
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "imperial",
                "cnt": 8  # 24 hours (3-hour intervals)
            }
            response = requests.get(url_v2, params=params_v2, timeout=30)

            if response.status_code != 200:
                print(f"  ✗ Error with fallback API: Status {response.status_code}")
                return []

            # Parse 2.5 API response
            data = response.json()
            hourly_data = []

            for item in data.get("list", []):
                dt = datetime.fromtimestamp(item["dt"])
                hourly_data.append({
                    "City": city_name,
                    "Time": dt.strftime("%I:%M %p"),
                    "Date": dt.strftime("%Y-%m-%d"),
                    "Temperature": f"{int(item['main']['temp'])}°",
                    "Feels Like": f"{int(item['main']['feels_like'])}°",
                    "Condition": item['weather'][0]['description'].title(),
                    "Precipitation": f"{int(item.get('pop', 0) * 100)}%",
                    "Humidity": f"{item['main']['humidity']}%",
                    "Wind": f"{int(item['wind']['speed'])} mph",
                    "Wind Direction": f"{item['wind'].get('deg', 0)}°"
                })

            print(f"  ✓ Fetched {len(hourly_data)} hourly entries")
            return hourly_data

        # Parse One Call API response
        data = response.json()
        hourly_data = []

        for hour in data.get("hourly", [])[:24]:  # Next 24 hours
            dt = datetime.fromtimestamp(hour["dt"])
            hourly_data.append({
                "City": city_name,
                "Time": dt.strftime("%I:%M %p"),
                "Date": dt.strftime("%Y-%m-%d"),
                "Temperature": f"{int(hour['temp'])}°",
                "Feels Like": f"{int(hour['feels_like'])}°",
                "Condition": hour['weather'][0]['description'].title(),
                "Precipitation": f"{int(hour.get('pop', 0) * 100)}%",
                "Humidity": f"{hour['humidity']}%",
                "Wind": f"{int(hour['wind_speed'])} mph",
                "Wind Direction": f"{hour['wind_deg']}°"
            })

        print(f"  ✓ Fetched {len(hourly_data)} hourly entries")
        return hourly_data

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def main():
    """Main function."""

    print("=" * 70)
    print("Hourly Weather Data Fetcher - OpenWeatherMap")
    print("=" * 70)
    print()

    # Check for API key
    if not API_KEY:
        print("⚠️  WARNING: No API key provided!")
        print("   Get a free key from: https://openweathermap.org/api")
        print("   Then set it in the script or as environment variable:")
        print("   export OPENWEATHER_API_KEY='your_key_here'")
        print()
        print("   For now, I'll try with the Weather.com location IDs approach...")
        print("=" * 70)
        return

    all_data = []

    for city, coords in CITIES.items():
        weather_data = fetch_hourly_weather(
            city,
            coords["lat"],
            coords["lon"],
            API_KEY
        )
        all_data.extend(weather_data)

    # Export to Excel
    if all_data:
        df = pd.DataFrame(all_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"hourly_weather_{timestamp}.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Hourly Weather', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['Hourly Weather']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                col_letter = chr(65 + idx)
                worksheet.column_dimensions[col_letter].width = max_length

        print()
        print("=" * 70)
        print(f"✓ SUCCESS! Weather data exported to: {output_file}")
        print(f"  Total entries: {len(all_data)}")
        print("=" * 70)

        # Preview
        print("\nPreview:")
        print(df.head(10).to_string())

    else:
        print("\n✗ No data was collected.")


if __name__ == "__main__":
    main()
