# Import essential libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load SpaceX data into a pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the Dash app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown for selecting a specific launch site or viewing all sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),

    html.Br(),

    # Pie chart for visualizing the success rates of launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Slider to filter data based on payload mass
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    # Scatter plot to display correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback to update pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Generate pie chart for all launch sites
        fig = px.pie(spacex_df, values='class', names='Launch Site',
                     title='Total Successful Launches By Site')
    else:
        # Generate pie chart for the selected launch site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df.groupby('class').count().reset_index()
        fig = px.pie(filtered_df, values='Unnamed: 0', names='class',
                     title=f'Total Launch Outcomes for {entered_site}')
    return fig

# Callback to update scatter plot based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        # Filter data by payload range for all sites
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
            title=f'Correlation Between Payload and Success (All Sites) - Payload: {payload_range[0]}kg to {payload_range[1]}kg'
        )
    else:
        # Filter data by payload range for the selected site
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
            title=f'Correlation Between Payload and Success ({entered_site}) - Payload: {payload_range[0]}kg to {payload_range[1]}kg'
        )
    return fig

# Start the Dash server
if __name__ == '__main__':
    app.run_server(debug=True)
