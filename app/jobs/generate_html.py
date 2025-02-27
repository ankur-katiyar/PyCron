import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def generate_html():
    try:
        with open("workdir/weather_data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Weather data file not found. Please run fetch_weather.py first.")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON from weather data file.")
        return

    # Print data structure for debugging
    print("Data keys:", list(data.keys()))
    if "daily" in data:
        print("Daily keys:", list(data["daily"].keys()))

    # Extract basic data that should always be present
    days = data["daily"]["time"]
    max_temps_c = data["daily"]["temperature_2m_max"]
    min_temps_c = data["daily"]["temperature_2m_min"]
    precipitation = data["daily"]["precipitation_sum"]
    
    # Handle potentially missing fields with defaults
    snowfall = data["daily"].get("snowfall_sum", [0] * len(days))
    wind_speed = data["daily"].get("wind_speed_10m_max", [0] * len(days))
    wind_direction = data["daily"].get("wind_direction_10m_dominant", [0] * len(days))
    uv_index = data["daily"].get("uv_index_max", [0] * len(days))
    
    # Print what we found for debugging
    print(f"Found snowfall data: {len(snowfall) > 0 and any(s > 0 for s in snowfall)}")
    print(f"Found UV index data: {len(uv_index) > 0 and any(u > 0 for u in uv_index)}")
    
    # Get AQI data if available
    aqi_data = []
    aqi_times = []
    
    if "air_quality" in data and "error" not in data["air_quality"]:
        print("Air quality data found")
        if "hourly" in data["air_quality"] and "us_aqi" in data["air_quality"]["hourly"]:
            aqi_hourly = data["air_quality"]["hourly"]["us_aqi"]
            aqi_times = data["air_quality"]["hourly"]["time"]
            print(f"AQI hourly data points: {len(aqi_hourly)}")
            
            # Calculate daily average AQI
            aqi_data = []
            for i in range(0, min(len(aqi_hourly), len(days) * 24), 24):
                daily_aqi = aqi_hourly[i:i+24]
                if daily_aqi:  # Check if there's data
                    valid_values = [x for x in daily_aqi if x is not None]
                    if valid_values:  # Check if there are valid values
                        aqi_data.append(np.mean(valid_values))
                    else:
                        aqi_data.append(0)
                else:
                    aqi_data.append(0)
            
            print(f"Calculated daily AQI data points: {len(aqi_data)}")
    else:
        print("No air quality data found or error in air quality data")
        if "air_quality" in data and "error" in data["air_quality"]:
            print(f"Air quality error: {data['air_quality']['error']}")

    # Convert temperatures to Fahrenheit
    max_temps_f = [c_to_f(temp) for temp in max_temps_c]
    min_temps_f = [c_to_f(temp) for temp in min_temps_c]

    # === Graph 1: Temperature Trends ===
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=days, y=max_temps_f, mode="lines+markers", 
                                  name="Max Temp (°F)", line=dict(color="red", width=3)))
    fig_temp.add_trace(go.Scatter(x=days, y=min_temps_f, mode="lines+markers", 
                                  name="Min Temp (°F)", line=dict(color="blue", width=3)))
    fig_temp.update_layout(title="14-Day Temperature Forecast (°F)", 
                           xaxis_title="Date", yaxis_title="Temperature (°F)",
                           template="plotly_dark", plot_bgcolor="#1e1e1e")

    # === Graph 2: Precipitation and Snowfall ===
    fig_precip = make_subplots(specs=[[{"secondary_y": True}]])
    fig_precip.add_trace(go.Bar(x=days, y=precipitation, name="Rain (mm)", 
                                marker_color="skyblue"), secondary_y=False)
    fig_precip.add_trace(go.Bar(x=days, y=snowfall, name="Snow (cm)", 
                                marker_color="white"), secondary_y=True)
    fig_precip.update_layout(title="14-Day Precipitation & Snowfall Forecast", 
                             xaxis_title="Date",
                             template="plotly_dark", plot_bgcolor="#1e1e1e",
                             barmode='group')
    fig_precip.update_yaxes(title_text="Rain (mm)", secondary_y=False)
    fig_precip.update_yaxes(title_text="Snow (cm)", secondary_y=True)

    # === Graph 3: Temperature Spread (Cool Effect) ===
    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(x=days, y=max_temps_f, 
                                    fill=None, mode="lines", line_color="red", name="Max Temp"))
    fig_spread.add_trace(go.Scatter(x=days, y=min_temps_f, 
                                    fill='tonexty', mode="lines", line_color="blue", name="Min Temp"))
    fig_spread.update_layout(title="Temperature Spread (Max vs Min °F)", 
                             xaxis_title="Date", yaxis_title="Temperature (°F)",
                             template="plotly_dark", plot_bgcolor="#1e1e1e")

    # === Graph 4: Wind Speed and Direction ===
    # Create a polar plot for wind direction
    fig_wind = make_subplots(rows=1, cols=2, 
                            specs=[[{"type": "xy"}, {"type": "polar"}]],
                            subplot_titles=("Wind Speed", "Wind Direction"))
    
    # Wind speed plot
    fig_wind.add_trace(go.Scatter(x=days, y=wind_speed, mode="lines+markers", 
                                 name="Wind Speed (km/h)", line=dict(color="cyan", width=3)),
                      row=1, col=1)
    
    # Wind direction polar plot
    fig_wind.add_trace(go.Barpolar(
        r=[1] * len(days),
        theta=wind_direction,
        marker_color=wind_speed,
        marker_colorscale="Viridis",
        marker_showscale=True,
        marker_colorbar_title="km/h",
        hovertext=[f"{days[i]}: {wind_speed[i]} km/h, {wind_direction[i]}°" for i in range(len(days))],
        name="Wind Direction"
    ), row=1, col=2)
    
    fig_wind.update_layout(title="14-Day Wind Forecast",
                          template="plotly_dark", plot_bgcolor="#1e1e1e",
                          height=500)

    # === Graph 5: UV Index ===
    fig_uv = go.Figure()
    
    # Create color scale for UV index
    uv_colors = []
    for uv in uv_index:
        if uv <= 2:
            color = "green"  # Low
        elif uv <= 5:
            color = "yellow"  # Moderate
        elif uv <= 7:
            color = "orange"  # High
        elif uv <= 10:
            color = "red"  # Very High
        else:
            color = "purple"  # Extreme
    
        uv_colors.append(color)
    
    fig_uv.add_trace(go.Bar(x=days, y=uv_index, name="UV Index", 
                           marker_color=uv_colors))
    
    # Add UV index categories
    fig_uv.add_shape(type="rect", x0=days[0], x1=days[-1], y0=0, y1=2, 
                    fillcolor="green", opacity=0.2, line_width=0)
    fig_uv.add_shape(type="rect", x0=days[0], x1=days[-1], y0=2, y1=5, 
                    fillcolor="yellow", opacity=0.2, line_width=0)
    fig_uv.add_shape(type="rect", x0=days[0], x1=days[-1], y0=5, y1=7, 
                    fillcolor="orange", opacity=0.2, line_width=0)
    fig_uv.add_shape(type="rect", x0=days[0], x1=days[-1], y0=7, y1=10, 
                    fillcolor="red", opacity=0.2, line_width=0)
    fig_uv.add_shape(type="rect", x0=days[0], x1=days[-1], y0=10, y1=15, 
                    fillcolor="purple", opacity=0.2, line_width=0)
    
    fig_uv.update_layout(title="14-Day UV Index Forecast",
                        xaxis_title="Date", yaxis_title="UV Index",
                        template="plotly_dark", plot_bgcolor="#1e1e1e")

    # === Graph 6: Air Quality Index (if available) ===
    fig_aqi = go.Figure()
    
    if aqi_data:
        # Create color scale for AQI
        aqi_colors = []
        for aqi in aqi_data:
            if aqi <= 50:
                color = "green"  # Good
            elif aqi <= 100:
                color = "yellow"  # Moderate
            elif aqi <= 150:
                color = "orange"  # Unhealthy for Sensitive Groups
            elif aqi <= 200:
                color = "red"  # Unhealthy
            elif aqi <= 300:
                color = "purple"  # Very Unhealthy
            else:
                color = "maroon"  # Hazardous
        
            aqi_colors.append(color)
        
        fig_aqi.add_trace(go.Bar(x=days[:len(aqi_data)], y=aqi_data, name="AQI", 
                               marker_color=aqi_colors))
        
        # Add AQI categories
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=0, y1=50, 
                        fillcolor="green", opacity=0.2, line_width=0)
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=50, y1=100, 
                        fillcolor="yellow", opacity=0.2, line_width=0)
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=100, y1=150, 
                        fillcolor="orange", opacity=0.2, line_width=0)
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=150, y1=200, 
                        fillcolor="red", opacity=0.2, line_width=0)
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=200, y1=300, 
                        fillcolor="purple", opacity=0.2, line_width=0)
        fig_aqi.add_shape(type="rect", x0=days[0], x1=days[-1], y0=300, y1=500, 
                        fillcolor="maroon", opacity=0.2, line_width=0)
        
        fig_aqi.update_layout(title="Air Quality Index Forecast",
                            xaxis_title="Date", yaxis_title="AQI (US)",
                            template="plotly_dark", plot_bgcolor="#1e1e1e")
    else:
        fig_aqi.add_annotation(text="AQI Data Not Available", 
                              xref="paper", yref="paper",
                              x=0.5, y=0.5, showarrow=False,
                              font=dict(size=20, color="white"))
        fig_aqi.update_layout(template="plotly_dark", plot_bgcolor="#1e1e1e")

    # Convert graphs to HTML
    temp_html = fig_temp.to_html(full_html=False)
    precip_html = fig_precip.to_html(full_html=False)
    spread_html = fig_spread.to_html(full_html=False)
    wind_html = fig_wind.to_html(full_html=False)
    uv_html = fig_uv.to_html(full_html=False)
    aqi_html = fig_aqi.to_html(full_html=False)

    # === Generate Final HTML Page ===
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Forecast - Attleboro, MA</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: white;
                text-align: center;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 90%;
                margin: auto;
                padding: 20px;
            }}
            h1 {{
                color: #00e5ff;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #80deea;
                margin-top: 40px;
                margin-bottom: 10px;
            }}
            p {{
                color: #b0bec5;
                margin-bottom: 30px;
            }}
            .graph-container {{
                margin-bottom: 50px;
                background-color: #1e1e1e;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }}
            .footer {{
                margin-top: 50px;
                padding: 20px;
                font-size: 0.8em;
                color: #78909c;
            }}
            .dashboard {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            @media (max-width: 1200px) {{
                .dashboard {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌤 Comprehensive Weather Forecast</h1>
            <p>14-Day Weather Outlook for Attleboro, MA (41.9445°N, 71.2856°W)</p>
            
            <h2>Temperature Trends</h2>
            <div class="graph-container">
                {temp_html}
            </div>
            
            <div class="dashboard">
                <div class="graph-container">
                    <h2>Temperature Range</h2>
                    {spread_html}
                </div>
                
                <div class="graph-container">
                    <h2>Precipitation & Snowfall</h2>
                    {precip_html}
                </div>
            </div>
            
            <h2>Wind Conditions</h2>
            <div class="graph-container">
                {wind_html}
            </div>
            
            <div class="dashboard">
                <div class="graph-container">
                    <h2>UV Index</h2>
                    {uv_html}
                </div>
                
                <div class="graph-container">
                    <h2>Air Quality</h2>
                    {aqi_html}
                </div>
            </div>
            
            <div class="footer">
                <p>Data provided by Open-Meteo API | Generated on {data['daily']['time'][0]}</p>
                <p>UV Index Categories: 0-2 (Low), 3-5 (Moderate), 6-7 (High), 8-10 (Very High), 11+ (Extreme)</p>
                <p>AQI Categories: 0-50 (Good), 51-100 (Moderate), 101-150 (Unhealthy for Sensitive Groups), 151-200 (Unhealthy), 201-300 (Very Unhealthy), 301+ (Hazardous)</p>
            </div>
        </div>
    </body>
    </html>
    """

    with open("workdir/weather.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Super cool comprehensive weather dashboard generated successfully!")

if __name__ == "__main__":
    generate_html()
