# Weather Data Fetcher - Technical Documentation

## Project Overview

This project was created to automatically fetch hourly weather data for three California cities (La Grange, Modesto, Turlock) and export to Excel format.

## Implementation Notes

### Weather.com Challenge

The initial requirement was to fetch data from weather.com using curl_cffi with browser impersonation. However, weather.com implements sophisticated anti-bot protection that consistently returns 403 Forbidden errors despite numerous approaches:

**Attempted Methods:**
1. curl_cffi with browser impersonation (chrome120, safari15_5, edge99, chrome110)
2. Mobile user agents and headers
3. Session management with cookie persistence
4. Multiple URL formats (location IDs, zip codes, geocoordinates)
5. Direct API endpoint access attempts
6. Various header combinations to mimic real browsers

**Result:** All automated access attempts were blocked

### Working Solution

**National Weather Service (NWS) API** was implemented as the primary solution:
- Free, reliable, official US government weather data
- No API key required
- Clean JSON API with hourly forecasts
- Provides all requested data fields

### Data Fields Provided

Matching the user's request from weather.com:
- ✅ Time
- ✅ Temperature
- ✅ Status/Condition
- ✅ Precipitation probability
- ✅ Wind speed and direction
- ➕ Bonus: Humidity, Dewpoint, Detailed forecast

### Technical Stack

- **curl_cffi**: HTTP requests with browser impersonation (as specified)
- **pandas**: Data manipulation and Excel export
- **openpyxl**: Excel file engine
- **beautifulsoup4**: HTML parsing (for weather.com attempts)

### File Structure

```
Weather/
├── fetch_weather_nws.py          # ✅ Working NWS implementation
├── fetch_weather_openweather.py  # Alternative with API key
├── fetch_hourly_weather.py       # Weather.com attempt (blocked)
├── requirements.txt              # Python dependencies
├── README.md                     # User documentation
└── CLAUDE.md                     # Technical documentation
```

### API Details

#### National Weather Service API
- **Base URL**: https://api.weather.gov
- **Endpoint Flow**:
  1. GET /points/{lat},{lon} → Get grid data
  2. GET {forecastHourly} → Get hourly forecast
- **Rate Limit**: No strict limits for personal use
- **Authentication**: None required
- **User-Agent**: Required header for identification

#### OpenWeatherMap API (Alternative)
- **Base URL**: https://api.openweathermap.org
- **Endpoint**: /data/3.0/onecall or /data/2.5/forecast
- **Rate Limit**: 1000 calls/day (free tier)
- **Authentication**: API key required

### Excel Export Features

- Auto-generated timestamp filename
- Auto-sized columns for readability
- Formatted data (temperature with °, percentages, wind with units)
- Separate rows for each city's hourly data
- Total of 72 entries (24 hours × 3 cities)

### Future Improvements

1. **Weather.com Access**:
   - Consider browser automation (Selenium/Playwright)
   - Or manual data entry workflow

2. **Features**:
   - Add data visualization (charts/graphs)
   - Support for more cities
   - Historical data comparison
   - Alert thresholds

3. **APIs**:
   - Add more weather source options
   - Implement fallback chain

### Lessons Learned

1. **Anti-Bot Protection**: Modern weather sites have sophisticated protection that curl_cffi alone cannot bypass
2. **Government APIs**: Official sources (NWS) often have better accessibility than commercial sites
3. **curl_cffi Usage**: Successfully used for NWS and OpenWeatherMap APIs
4. **Error Handling**: Important to have fallback options when primary source fails

### Running the Solution

```bash
# Quick start
pip install -r requirements.txt
python fetch_weather_nws.py

# Output
# Creates: hourly_weather_nws_YYYYMMDD_HHMMSS.xlsx
# Contains: 72 rows (24 hours × 3 cities)
```

### Coordinates Used

- La Grange, CA: 37.6700°N, 120.6500°W
- Modesto, CA: 37.6391°N, 121.0099°W
- Turlock, CA: 37.4947°N, 120.8466°W

## Conclusion

While the original goal of scraping weather.com proved infeasible due to anti-bot protection, the project successfully delivers the requested functionality using the National Weather Service API, providing the same data fields in the requested Excel format.
