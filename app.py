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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app: Dash = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Open connection to read cat_meals db
engine = db.create_engine('sqlite:///catmeals.sqlite', echo=False)
sql_DF = pd.read_sql("SELECT * FROM cat_meals", con=engine)
print(sql_DF)

# Style variables
colors = {'background': '#FFFFFF', 'text': '#111111'}

fig = go.Figure()
fig.add_trace(go.Scatter(x=sql_DF['next_meals'],
                         y=sql_DF['remaining_meals'],
                         name="Remaining cat meals",
                         line_color='deepskyblue',
                         opacity=1.0,
                         marker = dict(size = 20,
                                      color=[5, 4, 3, 2],
                                       colorscale='Blues'),
                         mode='markers'
                        ))

fig.update_layout(xaxis_range=[datetime.now() - timedelta(days=1),
                               datetime.now() + timedelta(days=1)],
                  title_text="",
                  xaxis_rangeslider_visible=True,
                  template = "plotly_white")

# Define app layout
app.layout = html.Div([
    # Title
    html.H1(
        children='CatMate Tracker',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),
    html.Div(id='output-container-button',
             children='Press Update! after filling the catmate...'),
    html.Br(),
    html.Label('Update button'),
    html.Button('Update!', id='button'),
    html.Br(),
    html.Br(),
    html.Label('Data'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in sql_DF.columns],
        data=sql_DF.to_dict('records'),
    ),
    html.Br(),
    html.Label('Update history'),
    dcc.Graph(id='live-graph', animate=True, figure=fig)
])


@app.callback(
    Output('output-container-button', 'children'),
    [Input('button', 'n_clicks')])
def update_output(n_clicks):
    return 'The button has been clicked {} times'.format(n_clicks)


if __name__ == '__main__':
    app.run_server(debug=False)
