import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from io import StringIO
import requests
# TODO : integrate bootstrap design library into layout

markdown_text = '''
# John's Food Diary

*Some days I am fat*\n
*Other days I am thinner*\n
*Every day I count*\n
A haiku by John Aiken

This is a data dashboard representing the food I eat on a daily basis. It uses the [plotly library dash](https://plot.ly/dash/) and google sheets as a database.

this should be rebuilt using this bootstrap library for dash

https://dash-bootstrap-components.opensource.faculty.ai/

lol, notes go here i guess
'''

def generate_table(dataframe, max_rows=10):
    dataframe = dataframe.reset_index()
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

s = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTx84fsp1moplR6uxUzYhMRxicBwJjxTGeW2kNyngbUme5r6kzhgWe8GMVC_Ve1QsiQ23_0HzRmdxBV/pub?gid=205792249&single=true&output=csv'
r = requests.get(s)
data = r.text
global df
df = pd.read_csv(StringIO(data))
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.set_index('Timestamp', inplace=True)

daily_calories = df.resample('D').sum()
daily_calories.columns = ['sum(calories)',]
daily_calories.sort_index(inplace=True)
    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Put down the fork!'

app.layout = html.Div(children=[
    # TODO : figure out how to print emoji (head should have utf-8)
    dcc.Markdown(children=markdown_text),

    html.H4(children='recent food'),
    generate_table(df.iloc[-10:]), # use only the most recent 10 items
    html.H1(children=''),

    html.Div(children='''
        Each point is the sum of the calories for the day. You can interact with the graph.
    '''),
    # TODO : write a line graph function to replace this
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                # {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'line', 'name': 'SF'},
                {'x': daily_calories.index, 'y': daily_calories['sum(calories)'], 'type': 'line', 'name': 'SF'},
                # {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'line', 'name': u'Montréal'},
                {'x': [daily_calories.index.min(), daily_calories.index.max()], 'y': [2000, 2000], 'type': 'line', 'name': u'You have eaten enough'},
            ],
            'layout': {
                'title': 'Calories per day'
            }
        }
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)

