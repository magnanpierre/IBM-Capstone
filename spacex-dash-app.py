# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites from the dataframe
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Create dropdown options - start with "All Sites" then add each launch site
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
dropdown_options.extend([{'label': site, 'value': site} for site in launch_sites])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div([
                                    html.Label("Launch Site:"),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=dropdown_options,
                                        value='ALL',
                                        placeholder='Select a Launch Site here',
                                        searchable=True
                                    )
                                ]),
                                html.Br(),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                     min=0,
                                    max=10000,
                                    step=1000,
                                    marks={i: f'{i}' for i in range(0, 10001, 1000)},  # Optional: adds labels
                                    value=[min_payload, max_payload]  # Current selected range
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # For ALL sites, we need to count the occurrences, not sum the values
        # Create a temporary dataframe with count of each class
        temp_df = spacex_df.copy()
        temp_df['class_label'] = temp_df['class'].map({0: 'Failed', 1: 'Success'})
        
        fig = px.pie(temp_df, names='class_label', title='Total Success Launches for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        filtered_df['class_label'] = filtered_df['class'].map({0: 'Failed', 1: 'Success'})
        fig = px.pie(filtered_df, names='class_label', title=f'Success Rate for {selected_site}')
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(site, payload):
    # Filter data
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload[0]) & 
        (spacex_df['Payload Mass (kg)'] <= payload[1])
    ]
    
    if site != 'ALL':
        df = df[df['Launch Site'] == site]
    
    # Create plot
    fig = px.scatter(
        df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',
        title='Payload vs. Mission Outcome',
        labels={
            'class': 'Launch Outcome',  # Renames the y-axis label
            'Payload Mass (kg)': 'Payload Mass (kg)',
            'Booster Version Category': 'Booster Version'
        }
    )
    
    # Make the y-axis show only 0 and 1 as "Failed" and "Success"
    fig.update_yaxes(
        tickvals=[0, 1],  # Only show ticks at 0 and 1
        ticktext=['Failed', 'Success']  # Label them properly
    )
    
    # Optional: Style improvements
    fig.update_traces(marker=dict(size=12, opacity=0.7))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run()