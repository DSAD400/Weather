#!/usr/bin/env python3
"""
Fetch hourly weather data using NOAA National Weather Service API and export to Excel.
This is a completely free alternative that doesn't require an API key.

NWS API: https://www.weather.gov/documentation/services-web-api
"""

from datetime import datetime
from curl_cffi import requests
import pandas as pd


# City coordinates
CITIES = {
    "La Grange, CA": {"lat": 37.6700, "lon": -120.6500},
    "Modesto, CA": {"lat": 37.6391, "lon": -121.0099},
    "Turlock, CA": {"lat": 37.4947, "lon": -120.8466}
}


def fetch_nws_hourly_weather(city_name, lat, lon):
    """
    Fetch hourly weather forecast from National Weather Service.

    Args:
        city_name: Name of the city
        lat: Latitude
        lon: Longitude

    Returns:
        List of hourly weather data dictionaries
    """
    print(f"Fetching weather for {city_name}...")

    headers = {
        'User-Agent': '(Weather Data Fetcher, contact@example.com)',  # NWS requires user agent
        'Accept': 'application/json'
    }

    try:
        # Step 1: Get the forecast grid endpoint for this location
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        response = requests.get(points_url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"  ✗ Error getting grid point: Status {response.status_code}")
            return []

        points_data = response.json()
        forecast_hourly_url = points_data['properties']['forecastHourly']

        # Step 2: Get hourly forecast
        response = requests.get(forecast_hourly_url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"  ✗ Error getting forecast: Status {response.status_code}")
            return []

        forecast_data = response.json()
        hourly_data = []

        for period in forecast_data['properties']['periods'][:24]:  # Next 24 hours
            dt = datetime.fromisoformat(period['startTime'].replace('Z', '+00:00'))

            # Extract wind speed and direction
            wind_speed = period.get('windSpeed', 'N/A')
            wind_direction = period.get('windDirection', 'N/A')
            wind = f"{wind_speed} {wind_direction}" if wind_speed != 'N/A' else 'N/A'

            # Precipitation probability
            precip_prob = period.get('probabilityOfPrecipitation', {}).get('value', 0)
            precip_prob = f"{precip_prob}%" if precip_prob else "0%"

            hourly_data.append({
                "City": city_name,
                "Time": dt.strftime("%I:%M %p"),
                "Date": dt.strftime("%Y-%m-%d"),
                "Temperature": f"{period['temperature']}°{period['temperatureUnit']}",
                "Condition": period['shortForecast'],
                "Detailed": period['detailedForecast'],
                "Precipitation": precip_prob,
                "Humidity": f"{period.get('relativeHumidity', {}).get('value', 'N/A')}%",
                "Wind": wind,
                "Dewpoint": f"{period.get('dewpoint', {}).get('value', 'N/A')}°"
            })

        print(f"  ✓ Fetched {len(hourly_data)} hourly entries")
        return hourly_data

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def main():
    """Main function."""

    print("=" * 70)
    print("Hourly Weather Data Fetcher - NOAA National Weather Service")
    print("=" * 70)
    print()

    all_data = []

    for city, coords in CITIES.items():
        weather_data = fetch_nws_hourly_weather(
            city,
            coords["lat"],
            coords["lon"]
        )
        all_data.extend(weather_data)

    # Export to Excel
    if all_data:
        df = pd.DataFrame(all_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"hourly_weather_nws_{timestamp}.xlsx"

        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Hourly Weather', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['Hourly Weather']
            for idx, col in enumerate(df.columns):
                max_length = min(
                    max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2,
                    50  # Max width
                )
                col_letter = chr(65 + idx) if idx < 26 else chr(65 + idx // 26 - 1) + chr(65 + idx % 26)
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
