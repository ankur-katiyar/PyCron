import json
import plotly.graph_objects as go

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def generate_html():
    with open("workdir/weather_data.json", "r") as f:
        data = json.load(f)

    days = data["daily"]["time"]
    max_temps_c = data["daily"]["temperature_2m_max"]
    min_temps_c = data["daily"]["temperature_2m_min"]
    precipitation = data["daily"]["precipitation_sum"]

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

    # === Graph 2: Precipitation Levels ===
    fig_precip = go.Figure()
    fig_precip.add_trace(go.Bar(x=days, y=precipitation, name="Precipitation (mm)", 
                                marker_color="skyblue"))
    fig_precip.update_layout(title="14-Day Precipitation Forecast", 
                             xaxis_title="Date", yaxis_title="Precipitation (mm)",
                             template="plotly_dark", plot_bgcolor="#1e1e1e")

    # === Graph 3: Temperature Spread (Cool Effect) ===
    fig_spread = go.Figure()
    fig_spread.add_trace(go.Scatter(x=days, y=max_temps_f, 
                                    fill=None, mode="lines", line_color="red", name="Max Temp"))
    fig_spread.add_trace(go.Scatter(x=days, y=min_temps_f, 
                                    fill='tonexty', mode="lines", line_color="blue", name="Min Temp"))
    fig_spread.update_layout(title="Temperature Spread (Max vs Min °F)", 
                             xaxis_title="Date", yaxis_title="Temperature (°F)",
                             template="plotly_dark", plot_bgcolor="#1e1e1e")

    # Convert graphs to HTML
    temp_html = fig_temp.to_html(full_html=False)
    precip_html = fig_precip.to_html(full_html=False)
    spread_html = fig_spread.to_html(full_html=False)

    # === Generate Final HTML Page ===
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Forecast</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #121212;
                color: white;
                text-align: center;
            }}
            .container {{
                width: 80%;
                margin: auto;
                padding: 20px;
            }}
            h1 {{
                color: cyan;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌤 14-Day Weather Forecast</h1>
            <p>Get an overview of temperature trends and precipitation levels.</p>
            {temp_html}
            {precip_html}
            {spread_html}
        </div>
    </body>
    </html>
    """

    with open("workdir/weather.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Super cool weather web page generated successfully!")

if __name__ == "__main__":
    generate_html()
