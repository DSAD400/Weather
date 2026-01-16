#!/usr/bin/env python3
"""
Fetch hourly weather data using NOAA National Weather Service API and export to Excel.
This is a completely free alternative that doesn't require an API key.

NWS API: https://www.weather.gov/documentation/services-web-api
"""

from datetime import datetime
from curl_cffi import requests
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


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
                "Precipitation": precip_prob,
                "Humidity": f"{period.get('relativeHumidity', {}).get('value', 'N/A')}%",
                "Wind": wind
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

            worksheet = writer.sheets['Hourly Weather']

            # Define styles
            header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_alignment = Alignment(horizontal='center', vertical='center')

            cell_alignment = Alignment(horizontal='center', vertical='center')
            border = Border(
                left=Side(style='thin', color='D0D0D0'),
                right=Side(style='thin', color='D0D0D0'),
                top=Side(style='thin', color='D0D0D0'),
                bottom=Side(style='thin', color='D0D0D0')
            )

            # Alternating row colors
            light_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')
            dark_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')

            # Style header row
            for col_num, column in enumerate(df.columns, 1):
                cell = worksheet.cell(row=1, column=col_num)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = border

            # Style data rows
            for row_num in range(2, len(df) + 2):
                # Alternate row colors
                row_fill = light_fill if row_num % 2 == 0 else dark_fill

                for col_num in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row_num, column=col_num)
                    cell.alignment = cell_alignment
                    cell.border = border
                    cell.fill = row_fill

            # Auto-adjust column widths
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 3
                col_letter = get_column_letter(idx + 1)
                worksheet.column_dimensions[col_letter].width = max_length

            # Set row height for better spacing
            for row in range(1, len(df) + 2):
                worksheet.row_dimensions[row].height = 20

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
