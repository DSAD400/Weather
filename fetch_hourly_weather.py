#!/usr/bin/env python3
"""
Fetch hourly weather data from weather.com for multiple cities and export to Excel.
Uses curl_cffi with browser impersonation to bypass restrictions.
"""

import json
import re
from datetime import datetime
from curl_cffi import requests
from bs4 import BeautifulSoup
import pandas as pd


# City configurations with their weather.com location IDs
# To find location IDs: Go to weather.com, search for the city, navigate to "Hourly Weather"
# and copy the long alphanumeric code from the URL after "/l/"
CITIES = {
    "La Grange, CA": "97e1932b93d87b2354c192acc960b9d375a080b85cd0896472365394f2f7bed6",
    "Modesto, CA": "",  # User needs to provide - see instructions below
    "Turlock, CA": "",  # User needs to provide - see instructions below
}

# INSTRUCTIONS TO FIND LOCATION IDs:
# 1. Open a web browser and go to https://weather.com
# 2. Search for "Modesto, CA" or "Turlock, CA"
# 3. Click on "Hourly Weather" or "Hour by Hour"
# 4. Copy the URL - it will look like: https://weather.com/weather/hourbyhour/l/XXXXXX...
# 5. The XXXXXX... part (long alphanumeric string) is the location ID
# 6. Add it to the CITIES dictionary above


def fetch_weather_data(location_id, city_name):
    """
    Fetch hourly weather data from weather.com for a specific location.

    Args:
        location_id: The weather.com location identifier
        city_name: Human-readable city name

    Returns:
        List of dictionaries containing hourly weather data
    """
    url = f"https://weather.com/weather/hourbyhour/l/{location_id}"

    print(f"Fetching weather data for {city_name}...")

    # Create session for maintaining cookies
    session = requests.Session()

    # More comprehensive headers to mimic a real browser
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
    }

    # Try with better browser impersonation and headers
    try:
        response = session.get(
            url,
            impersonate="chrome120",
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
    except Exception as e:
        print(f"Error fetching data for {city_name}: {e}")
        return []

    print(f"Status code: {response.status_code}")

    if response.status_code != 200:
        print(f"Error fetching data for {city_name}: Status {response.status_code}")
        # Try alternative browser profiles
        for browser in ["safari15_5", "edge99", "chrome110"]:
            print(f"  Retrying with {browser}...")
            try:
                response = session.get(
                    url,
                    impersonate=browser,
                    headers=headers,
                    timeout=30
                )
                if response.status_code == 200:
                    print(f"  Success with {browser}!")
                    break
            except:
                continue

        if response.status_code != 200:
            return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Weather.com typically embeds data in JSON within script tags
    hourly_data = []

    # Try to find JSON data in script tags
    script_tags = soup.find_all('script', type='application/ld+json')

    # Also look for data in script tags without type
    all_scripts = soup.find_all('script')

    # Try to extract hourly data from the page
    # Weather.com structure may vary, so we'll try multiple approaches

    # Approach 1: Look for hourly forecast table/details
    hourly_rows = soup.find_all('details', class_=re.compile('.*Disclosure.*'))
    if not hourly_rows:
        hourly_rows = soup.find_all('summary')

    # Approach 2: Look for data in JSON format within scripts
    for script in all_scripts:
        if script.string and 'hourly' in script.string.lower():
            try:
                # Try to extract JSON data
                text = script.string
                # Look for patterns that might contain hourly data
                json_match = re.search(r'({.*?"hourly".*?})', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(1))
                    # Process the JSON data
                    break
            except:
                continue

    # Approach 3: Parse HTML table/list structure
    # Look for hourly forecast containers
    forecast_container = soup.find('div', {'data-testid': 'HourlyForecast'})
    if not forecast_container:
        forecast_container = soup.find('section', class_=re.compile('.*hourly.*', re.I))

    if forecast_container:
        # Find all hourly entries
        hours = forecast_container.find_all(['li', 'div'], recursive=True, limit=24)

        for hour in hours[:24]:  # Get next 24 hours
            try:
                # Extract time
                time_elem = hour.find(['span', 'h3', 'p'], class_=re.compile('.*time.*|.*hour.*', re.I))
                if not time_elem:
                    time_elem = hour.find(['span', 'h3'])
                time_str = time_elem.get_text(strip=True) if time_elem else ""

                # Extract temperature
                temp_elem = hour.find(['span', 'div'], attrs={'data-testid': re.compile('.*emperature.*', re.I)})
                if not temp_elem:
                    temp_elem = hour.find(['span', 'div'], class_=re.compile('.*temp.*', re.I))
                if not temp_elem:
                    temp_elem = hour.find('span', string=re.compile(r'\d+°'))
                temp_str = temp_elem.get_text(strip=True) if temp_elem else ""

                # Extract condition/status
                condition_elem = hour.find(['span', 'div'], attrs={'data-testid': re.compile('.*phrase.*|.*condition.*', re.I)})
                if not condition_elem:
                    condition_elem = hour.find('img', alt=True)
                    if condition_elem:
                        condition_str = condition_elem.get('alt', '')
                    else:
                        condition_elem = hour.find(['span', 'p'], class_=re.compile('.*phrase.*|.*condition.*', re.I))
                        condition_str = condition_elem.get_text(strip=True) if condition_elem else ""
                else:
                    condition_str = condition_elem.get_text(strip=True)

                # Extract precipitation
                precip_elem = hour.find(['span', 'div'], attrs={'data-testid': re.compile('.*precip.*', re.I)})
                if not precip_elem:
                    precip_elem = hour.find(['span', 'div'], string=re.compile(r'\d+%'))
                precip_str = precip_elem.get_text(strip=True) if precip_elem else ""

                # Extract wind
                wind_elem = hour.find(['span', 'div'], attrs={'data-testid': re.compile('.*wind.*', re.I)})
                if not wind_elem:
                    wind_elem = hour.find(['span', 'div'], string=re.compile(r'\d+\s*(mph|MPH)'))
                wind_str = wind_elem.get_text(strip=True) if wind_elem else ""

                if time_str and temp_str:  # Only add if we have at least time and temp
                    hourly_data.append({
                        'City': city_name,
                        'Time': time_str,
                        'Temperature': temp_str,
                        'Condition': condition_str,
                        'Precipitation': precip_str,
                        'Wind': wind_str
                    })
            except Exception as e:
                continue

    print(f"Found {len(hourly_data)} hourly entries for {city_name}")
    return hourly_data


def find_location_id(city_name, state="CA"):
    """
    Search for a city's location ID on weather.com.

    Args:
        city_name: Name of the city
        state: State abbreviation (default: CA)

    Returns:
        Location ID string or None
    """
    search_query = f"{city_name}, {state}"
    search_url = f"https://weather.com/search/enhancedlocalsearch?where={search_query.replace(' ', '+')}"

    print(f"Searching for location ID for {search_query}...")

    try:
        response = requests.get(
            search_url,
            impersonate="chrome110",
            timeout=30
        )

        if response.status_code == 200:
            # Try to extract location from redirect or response
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for links to hourly forecast
            links = soup.find_all('a', href=re.compile(r'/weather/hourbyhour/l/'))
            if links:
                href = links[0].get('href')
                location_id = href.split('/l/')[-1]
                print(f"Found location ID for {city_name}: {location_id}")
                return location_id

            # Alternative: look for JSON data with location info
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'location' in script.string.lower():
                    # Try to extract location ID from JSON
                    match = re.search(r'"geocode":\s*"([^"]+)"', script.string)
                    if match:
                        location_id = match.group(1)
                        print(f"Found location ID for {city_name}: {location_id}")
                        return location_id
    except Exception as e:
        print(f"Error searching for {city_name}: {e}")

    return None


def main():
    """Main function to fetch weather data and export to Excel."""

    print("=" * 60)
    print("Hourly Weather Data Fetcher for California Cities")
    print("=" * 60)
    print()

    # First, find location IDs for cities that don't have them
    for city in CITIES:
        if CITIES[city] is None:
            city_name = city.split(',')[0].strip()
            location_id = find_location_id(city_name)
            if location_id:
                CITIES[city] = location_id
            else:
                print(f"Warning: Could not find location ID for {city}")

    print()
    print("Fetching weather data...")
    print()

    # Fetch weather data for all cities
    all_data = []

    for city, location_id in CITIES.items():
        if location_id:
            weather_data = fetch_weather_data(location_id, city)
            all_data.extend(weather_data)
        else:
            print(f"Skipping {city} - no location ID available")

    # Create DataFrame and export to Excel
    if all_data:
        df = pd.DataFrame(all_data)

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"hourly_weather_{timestamp}.xlsx"

        # Export to Excel
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Hourly Weather', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['Hourly Weather']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length

        print()
        print("=" * 60)
        print(f"SUCCESS! Weather data exported to: {output_file}")
        print(f"Total entries: {len(all_data)}")
        print("=" * 60)

        # Display preview
        print("\nPreview of data:")
        print(df.head(10).to_string())

    else:
        print("\nNo data was collected. Please check the city URLs and try again.")


if __name__ == "__main__":
    main()
