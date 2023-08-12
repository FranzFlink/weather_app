import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import requests
import pandas 
import time
# Initialize the Dash app with Bootstrap for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the path to the CSV file
csv_path = "/home/josh/python_scripts/weather_app/weather_data.csv"

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import requests
import time
import threading

# Initialize the Dash app with Bootstrap for styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the URL and parameters
url = 'https://api.weather.com/v2/pws/observations/current?apiKey=e1f10a1e78da46f5b10a1e78da96f525&stationId=IPRESS33&format=json&units=m'

# Define the path to the CSV file
csv_path = "weather_data.csv"

# Fetch the data
def fetch_weather_data():
    response = requests.get(url)
    data = response.json()
    return data['observations'][0]['metric']

# Function to fetch data and write to CSV
def fetch_and_write():
    while True:
        data = fetch_weather_data()
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        new_data = pd.DataFrame([{'timestamp': current_time}])
        new_data = pd.concat([new_data, pd.DataFrame([data])], axis=1)
        
        df = pd.read_csv(csv_path)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(csv_path, index=False)
        
        time.sleep(120)

# Start the data collection in a separate thread
def fetch_data_continuously():
    # Check if the CSV file exists and if not, create it with headers
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['timestamp'] + list(fetch_weather_data().keys()))
        df.to_csv(csv_path, index=False)
    
    fetch_and_write()

threading.Thread(target=fetch_data_continuously).start()



# Layout of the dashboard
app.layout = dbc.Container([
    html.H1("Weather Data", className="mb-4"),
    
    dcc.Dropdown(
        id='weather-metric-dropdown',
        options=[{'label': key, 'value': key} for key in pd.read_csv(csv_path).columns if key != 'timestamp'],
        value='temp',
        clearable=False,
        className="mb-4"
    ),
    
    dcc.Graph(id='weather-data-graph'),
    
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update the graph
@app.callback(
    Output('weather-data-graph', 'figure'),
    [Input('weather-metric-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graph(metric, n):
    df = pd.read_csv(csv_path)
    return {
        'data': [go.Scatter(
            x=df['timestamp'],
            y=df[metric],
            mode='lines+markers'
        )],
        'layout': go.Layout(
            title=f'Time Series of {metric}',
            xaxis={'title': 'Timestamp'},
            yaxis={'title': 'Value'},
            showlegend=False
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
