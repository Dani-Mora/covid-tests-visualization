import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import (
    Input,
    Output
)

from geo import geojson_data
from data import (
    latest_data,
    daily_tests,
    daily_positive_rates,
    tests_per_abs
)

import pytz
import datetime


geo_data = geojson_data()
timezone = pytz.timezone('Europe/Berlin')
source_code_url = 'https://github.com/Dani-Mora/covid-tests-visualization'

app = dash.Dash()
server = app.server

last_update_time = datetime.datetime.now()
current_df = latest_data()


def _daily_info_plot() -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    daily_tests_df = daily_tests(current_df)
    fig.add_trace(go.Scatter(x=daily_tests_df.Data,
                             y=daily_tests_df.Tests,
                             mode='markers',
                             name='Tests'),
                  secondary_y=False)

    daily_rates_df = daily_positive_rates(current_df)
    fig.add_trace(go.Scatter(x=daily_rates_df.Data,
                             y=daily_rates_df['Percentatge positious'],
                             mode='markers',
                             name='Positius (%)'),
                  secondary_y=True)

    fig.update_xaxes(title_text='Data')
    fig.update_yaxes(title_text='Tests', secondary_y=False)
    fig.update_yaxes(title_text='Positius (%)',
                     secondary_y=True)

    fig.update_layout(title='Dades diàries',
                      autosize=True,
                      hovermode="x unified",
                      legend_orientation="h")
    return fig


def _map_plot() -> go.Figure:
    df = tests_per_abs(current_df)
    fig = go.Figure(go.Choroplethmapbox(geojson=geo_data,
                                        locations=df.ABSCodi,
                                        text=df.ABSDescripcio,
                                        colorscale='Greens',
                                        hovertemplate='%{text}<extra>%{z}</extra>',
                                        z=df.TotalTests))


    fig.update_layout(mapbox_style='carto-positron',
                      mapbox_center={'lat': 41.75, 'lon': 2.10},
                      mapbox_zoom=7.25,
                      autosize=True)

    return fig


def _last_update_text():
    cat_time = timezone.localize(last_update_time)
    cat_str_time = cat_time.strftime('%Y-%m-%d %H:%M:%S')
    return [html.H3(f'Darrera actualització: {cat_str_time}, CEST (UTC+2)')]


# Define page structure
title = html.Div([html.H1('COVID-19 tests realitzats a Catalunya')],
                 style={'textAlign': 'center', 'padding-bottom': '30'})

last_update = html.Div(id='last-updated-text',
                       children=_last_update_text(),
                       style={'textAlign': 'center', 'padding-bottom': '10'})

source_code = html.Div(
    [html.H5(html.A(href=source_code_url, children='Codi font'))],
    style={'textAlign': "left", 'padding-left': '5vw'}
)

timer = dcc.Interval(
    id='interval-component',
    interval=2*60*60*1000, # Update every 2 hours (ms)
    n_intervals=0
)

main_div = html.Div([
    dcc.Graph(
        id='main-graph',
        figure=_map_plot(),
        style={'width': '100vw', 'height': '60vh'}),
    dcc.Graph(
        id='daily-plot-graph',
        figure=_daily_info_plot(),
        style={'width': '100vw', 'height': '40vh'})
])

app.layout = html.Div([
    title,
    last_update,
    main_div,
    source_code,
    timer
])


@app.callback([
    Output(component_id='daily-plot-graph', component_property='figure'),
    Output(component_id='main-graph', component_property='figure'),
    Output(component_id='last-updated-text', component_property='children')],
    [Input(component_id='interval-component', component_property='n_intervals')]
)
def update_app(n):
    print(f'Update plot: {n}')
    global last_update_time
    last_update_time = datetime.datetime.now()
    global current_df
    current_df = latest_data()
    return _daily_info_plot(), _map_plot(), _last_update_text()


if __name__ == '__main__':
    app.run_server(debug=True)
