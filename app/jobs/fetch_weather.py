import requests
import json

API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 41.9445,  # Example: Attleboro, MA
    "longitude": -71.2856,
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    "timezone": "auto",
    "forecast_days": 14
}

def fetch_weather():
    response = requests.get(API_URL, params=PARAMS)
    if response.status_code == 200:
        data = response.json()
        with open("workdir/weather_data.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Weather data saved successfully!")
    else:
        print("Failed to fetch weather data:", response.status_code)

if __name__ == "__main__":
    fetch_weather()
