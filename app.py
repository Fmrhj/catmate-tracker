# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
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
import cat_modules
import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app: Dash = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Open connection to read cat_meals db
engine = db.create_engine('sqlite:///catmeals.sqlite', echo=False)
sql_DF = pd.read_sql("SELECT * FROM cat_meals", con=engine)
sql_DF = sql_DF.drop('index', axis=1)


# Check the time format
sql_DF['next_meals'] = pd.to_datetime(sql_DF['next_meals'], format="%Y-%m-%d %H:%M:%S")
print(sql_DF)

# Style variables
colors = {'background': '#FFFFFF', 'text': '#111111', 'general': 'RoyalBlue'}

fig = go.Figure()
fig.add_trace(go.Scatter(x=sql_DF['next_meals'],
                         y=sql_DF['remaining_meals'],
                         name="Remaining cat meals",
                         opacity=1.0,
                         marker=dict(size=30,
                                     line=dict(color="black"),
                                     symbol='x'),
                         mode='markers',
                         # visible='legendonly',
                         hovertemplate="date: %{x}<br>remaining meals: %{y}<extra></extra>"))

fig.update_layout(xaxis_range=[datetime.now() - timedelta(days=1),
                               datetime.now() + timedelta(days=1)],
                  title_text="",
                  template="plotly_white")

fig.add_shape(
    dict(
        type="line",
        x0=datetime.now(),
        y0=0,
        x1=datetime.now(),
        y1=4.5,
        line=dict(
            color=colors['general'],
            width=3
        )
    ))

fig.add_trace(go.Scatter(
    x=[datetime.now().strftime("%Y-%m-%d %H:%M")],
    y=[-0.5],
    text=["Now"],
    mode="text",
    showlegend=False
))


# Define app layout
app.layout = html.Div([
        # Title
        html.H1(
            children='Catmate Tracker',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
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
        # Update button container
        html.Div(id='output-container-button',
                 children='Press Update! after filling the catmate...',
                 style={'textAlign': 'center'}),
        html.Br(),
        html.Div(
            children=[dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i, "selectable": True} for i in sql_DF.columns],
                data=sql_DF.to_dict('records'),
                editable=False,
                style_as_list_view=True,
                style_cell={'padding': '5px', 'textAlign': 'left'},
                style_cell_conditional=[{'if': {'column_id': 'remaining_meals'}, 'textAlign': 'center'}],
                sort_action="native",
                page_action="native",
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[{
                    "if": {'column_id': str(x),
                           # create the filter query JS + python. Really important: use the JS time format
                           'filter_query': '{next_meals} > ' + datetime.now().strftime("%Y-%m-%d") +
                                           'T' + datetime.now().strftime("%H:%M:%S")
                           },
                    "backgroundColor": colors['general'],
                    'color': 'white'} for x in sql_DF.columns
                ]
            )],
            className='row'
        ),

        html.Br(),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-graph', animate=True, figure=fig),
        dcc.Interval(id='interval-component', interval=30 * 1000, n_intervals=0),
        html.Hr(),
        dcc.Markdown(f'''v0.1
{datetime.now().strftime("%B %Y")}

Check the project in [GitHub/Fmrhj](https://github.com/Fmrhj/catmate-tracker) 
''',
                     style={'textAlign': 'center'})
    ])

#app.layout = serve_layout

# Button update
@app.callback(
    Output('output-container-button', 'children'),
    [Input('button', 'n_clicks')])
def update_output(n_clicks):
    return 'The button has been clicked {} times'.format(n_clicks)

# Actual time
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    style = {'padding': '5px', 'fontSize': '20px'}
    return [
        html.Span(f'Actual Time: {datetime.now().strftime("%Y-%m-%d %H:%M")}', style=style),
    ]

if __name__ == '__main__':
    app.run_server(debug=True)
