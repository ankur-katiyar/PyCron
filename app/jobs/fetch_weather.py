import requests
import json
import os

API_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 41.9445,  # Example: Attleboro, MA
    "longitude": -71.2856,
    "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", 
              "snowfall_sum", "wind_speed_10m_max", "wind_direction_10m_dominant",
              "uv_index_max"],
    "timezone": "auto",
    "forecast_days": 14,
    "current_weather": True,
}

def fetch_weather():
    # First fetch weather data including snow, wind, and UV
    print("Fetching main weather data...")
    response = requests.get(API_URL, params=PARAMS)
    
    if response.status_code == 200:
        data = response.json()
        print("Main weather data fetched successfully.")
        
        # Fetch AQI data from air quality endpoint
        print("Fetching air quality data...")
        aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        aqi_params = {
            "latitude": PARAMS["latitude"],
            "longitude": PARAMS["longitude"],
            "hourly": ["us_aqi", "pm10", "pm2_5"],
            "timezone": PARAMS["timezone"]
        }
        
        try:
            aqi_response = requests.get(aqi_url, params=aqi_params)
            if aqi_response.status_code == 200:
                aqi_data = aqi_response.json()
                print("Air quality data fetched successfully.")
                # Merge AQI data with weather data
                data["air_quality"] = aqi_data
            else:
                print(f"Failed to fetch AQI data: {aqi_response.status_code}")
                print(f"Response: {aqi_response.text}")
                data["air_quality"] = {"error": f"Failed with status code {aqi_response.status_code}"}
        except Exception as e:
            print(f"Exception while fetching AQI data: {str(e)}")
            data["air_quality"] = {"error": str(e)}
        
        # Create workdir if it doesn't exist
        os.makedirs("workdir", exist_ok=True)
        
        # Save combined data
        with open("workdir/weather_data.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Weather data saved successfully!")
        
        # Print available fields for debugging
        print("\nAvailable fields in the data:")
        if "daily" in data:
            print("Daily fields:", list(data["daily"].keys()))
        if "air_quality" in data and "hourly" in data["air_quality"]:
            print("Air quality fields:", list(data["air_quality"]["hourly"].keys()))
    else:
        print(f"Failed to fetch weather data: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    fetch_weather()
