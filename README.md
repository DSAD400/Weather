# Hourly Weather Data Fetcher

Automated tool to fetch hourly weather forecasts for California cities and export to Excel format.

## 📋 Overview

This project fetches 24-hour weather forecasts for:
- **La Grange, CA**
- **Modesto, CA**
- **Turlock, CA**

Data includes: Time, Temperature, Weather Condition, Precipitation %, Humidity, and Wind

## ✅ Working Solution: National Weather Service (NWS)

**Use this script:** `fetch_weather_nws.py`

### Features
- ✅ **100% Free** - No API key required
- ✅ **Reliable** - Uses NOAA's official weather data
- ✅ **Complete Data** - Time, temp, conditions, precipitation, humidity, wind
- ✅ **Excel Output** - Formatted .xlsx file with auto-sized columns

### Usage

```bash
python fetch_weather_nws.py
```

Output: `hourly_weather_nws_YYYYMMDD_HHMMSS.xlsx`

### Sample Output

| City | Time | Date | Temperature | Condition | Precipitation | Humidity | Wind |
|------|------|------|-------------|-----------|---------------|----------|------|
| La Grange, CA | 11:00 AM | 2026-01-16 | 53°F | Areas Of Fog | 0% | 91% | 2 mph SSE |
| La Grange, CA | 12:00 PM | 2026-01-16 | 56°F | Mostly Sunny | 0% | 85% | 2 mph S |
| Modesto, CA | 11:00 AM | 2026-01-16 | 54°F | Partly Sunny | 0% | 89% | 3 mph SE |

---

## ⚠️ Weather.com Status

### Issue
`fetch_hourly_weather.py` was designed to scrape weather.com using curl_cffi with browser impersonation, but weather.com has strong anti-bot protection that returns **403 Forbidden** errors for all automated access attempts.

### What Was Tried
- ✓ curl_cffi with multiple browser impersonations (chrome120, safari15_5, edge99)
- ✓ Mobile user agents
- ✓ Session management with cookies
- ✓ Various HTTP headers configurations
- ✓ Different URL formats (zip codes, coordinates, location IDs)
- ✓ API endpoint attempts

**Result:** All attempts blocked with 403 errors

### Alternative If You Need Weather.com Data

**Manual Method:**
1. Open browser, go to https://weather.com
2. Search for each city
3. Navigate to "Hourly Weather"
4. Copy location ID from URL: `/l/LOCATION_ID`
5. Update `fetch_hourly_weather.py` with location IDs

**OpenWeatherMap Alternative:**
- Use `fetch_weather_openweather.py`
- Requires free API key from: https://openweathermap.org/api
- Set environment variable: `export OPENWEATHER_API_KEY='your_key'`

---

## 🔧 Installation

### Requirements
```bash
pip install curl_cffi beautifulsoup4 pandas openpyxl
```

Or:
```bash
pip install -r requirements.txt
```

### Dependencies
- **curl_cffi** - HTTP requests with browser impersonation
- **beautifulsoup4** - HTML parsing (for weather.com attempts)
- **pandas** - Data manipulation
- **openpyxl** - Excel file generation

---

## 📁 Files

| File | Description | Status |
|------|-------------|--------|
| `fetch_weather_nws.py` | ✅ **Working** - Uses NWS API | **Use This** |
| `fetch_weather_openweather.py` | ✅ Works with API key | Alternative |
| `fetch_hourly_weather.py` | ❌ Blocked by weather.com | Not working |
| `find_location_ids.py` | Helper to find location IDs | Testing |
| `requirements.txt` | Python dependencies | - |

---

## 🚀 Quick Start

**Recommended Workflow:**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the NWS fetcher (no setup needed)
python fetch_weather_nws.py

# 3. Open the generated Excel file
# File will be: hourly_weather_nws_YYYYMMDD_HHMMSS.xlsx
```

---

## 📊 Data Fields

### NWS Output
- **City** - City name
- **Time** - Hour (12-hour format)
- **Date** - ISO date (YYYY-MM-DD)
- **Temperature** - Degrees Fahrenheit
- **Condition** - Weather description (Sunny, Cloudy, etc.)
- **Detailed** - Detailed forecast text
- **Precipitation** - Probability of precipitation (%)
- **Humidity** - Relative humidity (%)
- **Wind** - Wind speed and direction
- **Dewpoint** - Dewpoint temperature

---

## 🌐 API Sources

### National Weather Service (NWS)
- **API**: https://api.weather.gov
- **Documentation**: https://www.weather.gov/documentation/services-web-api
- **Cost**: Free
- **Key Required**: No
- **Rate Limit**: Reasonable (no strict limits for personal use)
- **Coverage**: USA only

### OpenWeatherMap (Alternative)
- **API**: https://openweathermap.org/api
- **Cost**: Free tier available (1000 calls/day)
- **Key Required**: Yes
- **Coverage**: Global

---

## 🛠️ Troubleshooting

### "ModuleNotFoundError"
```bash
pip install curl_cffi beautifulsoup4 pandas openpyxl
```

### NWS API Returns Errors
- Check your internet connection
- Verify coordinates are correct
- NWS API may be temporarily down (rare)

### Want Different Cities?
Edit the `CITIES` dictionary in any script:
```python
CITIES = {
    "Your City, CA": {"lat": XX.XXXX, "lon": -XXX.XXXX}
}
```

Find coordinates at: https://www.latlong.net

---

## 📝 Notes

- **Weather.com scraping** is not reliable due to anti-bot protection
- **NWS API** is the recommended free solution for US locations
- All scripts use curl_cffi for HTTP requests as specified in project requirements
- Excel files include auto-sized columns for readability
- Timestamps in filenames prevent overwriting previous data

---

## 📄 License

This project is provided as-is for educational and personal use.

---

## 🤝 Contributing

To improve this project:
1. Test alternative methods for weather.com access
2. Add support for more cities
3. Implement additional weather APIs
4. Add data visualization features

---

**Last Updated:** January 16, 2026
**Status:** ✅ Working with NWS API
