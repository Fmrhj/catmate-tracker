# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
from dash import Dash
import sqlalchemy as db
import pandas as pd
import dash_table
from textwrap import dedent as d
import plotly
import plotly.graph_objects as go
from datetime import datetime
from datetime import timedelta
from collections import deque
import cat_modules as cats
import dash_bootstrap_components as dbc
import numpy as np
import sqlite3
import os
import time

# Global variables
os.environ['TZ'] = 'Europe/Berlin'
standard_date_format = "%Y-%m-%d %H:%M:%S"
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Style variables
colors = {'background': '#FFFFFF', 'text': '#111111', 'general': 'RoyalBlue'}

# SQL lite URI
db_uri = "sqlite:///catmeals.sqlite"

app: Dash = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Open connection to read cat_meals db
def get_data(target_db_uri):
    engine = db.create_engine(target_db_uri, echo=False)
    tmp_table = pd.read_sql("SELECT * FROM cat_meals", con=engine)
    tmp_table['next_meals'] = pd.to_datetime(tmp_table['next_meals'].str.strip(), format=standard_date_format)
    tmp_table = tmp_table.drop('index', axis=1)

    # Get just the last 4 records
    tmp_table = tmp_table.iloc[-4:]

    # Check the time format
    print("[STATUS] Actual future meal records:")
    print(tmp_table)
    return tmp_table


def generate_plot(data_frame_input):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_frame_input['next_meals'],
                             y=data_frame_input['remaining_meals'],
                             name="Remaining cat meals",
                             marker=dict(size=30,
                                         line=dict(color="black"),
                                         symbol='x'),
                             mode='markers',
                             hovertemplate="date: %{x}<br>remaining meals: %{y}<extra></extra>"))

    fig.update_layout(xaxis_range=[datetime.now() - timedelta(days=1),
                                   datetime.now() + timedelta(days=1)],
                      title_text="",
                      template="plotly_white")

    fig.add_shape(
        dict(type="line",
             x0=datetime.now(),
             y0=0,
             x1=datetime.now(),
             y1=4.5,
             line=dict(color=colors['general'], width=3)
             ))

    fig.add_trace(go.Scatter(
        x=[datetime.now().strftime("%Y-%m-%d %H:%M")],
        y=[-0.5],
        text=["Now"],
        mode="text",
        showlegend=False
    ))

    return fig


# Define app layout
app.layout = html.Div([

    html.Div([

        # Erich
        html.Div(html.Img(src=app.get_asset_url("img_cat_stick_erich.jpg"), style={"width": "100%"}),
                 className="two columns"),

        # Title
        html.Div([

            # Title
            html.H1(children=['Catmate Tracker'],
                     style={'textAlign': 'center',
                            'color': colors['text']}),

             # Markdown description
             dcc.Markdown('''
             A web application for tracking the [catmate](https://pet-mate.com/gb/product/c300-automatic-pet-feeder-with-digital-timer/) status
             ''',
                          style={'textAlign': 'center'}),

             # Update button container
             html.Div(html.Button('Update!',
                                  id='button',
                                  style={'textAlign': 'center'}),
                      style={'textAlign': 'center'}
                      ),

             html.Div(id="recent-update", style={'textAlign': 'center'})

             ],
            className="eight columns"),

        # Rieke
        html.Div(html.Img(src=app.get_asset_url("img_cat_stick_rieke_1.jpg"),
                          style={"width": "100%", "textAlign": "left"})
                 , className="two columns")

    ], className="row"),



    html.Br(),
    # Update button container
    html.Div(id='output-container-button',
             children='Press Update! after filling the catmate...',
             style={'textAlign': 'center'}),

    html.Div(
        children=[dash_table.DataTable(
            id='table',
            editable=False,
            style_as_list_view=True,
            style_cell={'padding': '5px', 'textAlign': 'left'},
            style_cell_conditional=[{'if': {'column_id': 'remaining_meals'}, 'textAlign': 'center'}],
            sort_action="native",
            page_action="native",
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )],
        className='row'
    ),

    html.Br(),

    html.Div(id='live-update-text'),

    dcc.Graph(id='live-graph', animate=True),

    html.Div(id="new-records", style={'textAlign': 'center'}),

    # Interval component: serves just to refresh the application

    dcc.Interval(id='interval-component', interval=30 * 1000, n_intervals=0),

    html.Hr(),

    dcc.Markdown(f'''v1.1
{datetime.now().strftime("%B %Y")}

Check the project in [GitHub/Fmrhj](https://github.com/Fmrhj/catmate-tracker) 
''',
                 style={'textAlign': 'center'})
])


# app.layout = serve_layout


# Button update
@app.callback(
    Output('output-container-button', 'children'),
    [Input('button', 'n_clicks')])
def update_output(n_clicks):
    msg = ""
    if n_clicks is not None:
        msg = "Table has been successfully updated!"
    return msg


# Actual time
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '20px'}
    return [
        html.Span(f'Actual Time in Berlin: {datetime.now().strftime("%Y-%m-%d %H:%M")}', style=style),
    ]


@app.callback(
    Output("new-records", "children"),
    [Input("button", "n_clicks")])
def add_and_show_records(n):

    if n is not None:
        # Create new pandas data frame with future meals
        new_records = cats.generate_next_meals_table()
        print("[UPDATE] New meals!")
        print(new_records)

        # Open connection
        engine = db.create_engine(db_uri, echo=False)
        conn = engine.connect()

        # Write results
        new_records.to_sql("cat_meals", conn, if_exists="append")

        # Close connection
        conn.close()

    return html.Span("")


@app.callback([
    Output("recent-update", "children"), Output("button", "style")],
    [Input('interval-component', 'n_intervals')])
def check_recent_update(n):
    tmp_check = get_data(db_uri)
    # Extract last time_stamp value
    last_value = tmp_check['time_stamp'][tmp_check.index[-1]]
    msg = ""

    # Active button
    button_display = dict()

    # Check if the table has been update recently, i.e. in the last 2 hours
    check_boolean = datetime.now() < datetime.strptime(last_value, standard_date_format) + timedelta(hours=12)

    if check_boolean:
        msg = "Meals have been updated in the last 12 hours"
        button_display = dict(display="none")

    return msg, button_display


# plot callback
@app.callback([
    Output('live-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_plot(n):
    # Get data from sqllite
    tmp_data = get_data(db_uri)
    return [generate_plot(tmp_data)]

# table callback
# plot callback
@app.callback(
    [Output('table', 'data'),
     Output('table', 'columns'),
     Output('table', 'style_data_conditional')
     ],
    [Input('interval-component', 'n_intervals')]
)
def update_table(n):
    # Get data from sqllite
    tmp_data = get_data(db_uri)

    columns = [{"name": i, "id": i, "selectable": True} for i in tmp_data.columns]
    data = tmp_data.to_dict('records')
    style_data_conditional = [{
        "if": {'column_id': str(x),
               # create the filter query JS + python. Really important: use the JS time format
               'filter_query': '{next_meals} > ' + datetime.now().strftime("%Y-%m-%d") +
                               'T' + datetime.now().strftime("%H:%M:%S")
               },
        "backgroundColor": colors['general'],
        'color': 'white'} for x in tmp_data.columns
    ]

    return data, columns, style_data_conditional


if __name__ == '__main__':
    app.run_server(debug=True)
