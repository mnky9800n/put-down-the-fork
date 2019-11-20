import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from io import StringIO
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

# TODO : integrate bootstrap design library into layout

markdown_text = '''
*Some days I am fat*
*Other days I am thinner*\n
*Every day I count*\n
A haiku by John Aiken

This is a data dashboard representing the food I eat on a daily basis. It uses the [plotly library dash](https://plot.ly/dash/) and google sheets as a database.

this should be rebuilt using this bootstrap library for dash
lol, notes go here i guess
'''


#####
# gets data from google spreadsheet and puts in pandas dataframe
s = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTx84fsp1moplR6uxUzYhMRxicBwJjxTGeW2kNyngbUme5r6kzhgWe8GMVC_Ve1QsiQ23_0HzRmdxBV/pub?gid=205792249&single=true&output=csv'
r = requests.get(s)
data = r.text
global df
df = pd.read_csv(StringIO(data))
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df.set_index('Timestamp', inplace=True)

#####
# converts data to daily format
daily_calories = df.resample('D').sum()
daily_calories.columns = ['sum(calories)',]
daily_calories.sort_index(inplace=True)

#####
# calendar
# TODO : make a calendar function that is dynamic and isnt terrible like this one
year_df = pd.date_range('1/1/2019', periods=365, freq='D')
year_df = pd.DataFrame(index=year_df)
test = year_df.join(daily_calories)
test_series = pd.Series(test.values[:,0], index=test.index)
fig, ax = plt.subplots(figsize=(15, 5))
calmap.yearplot(test_series, year=2019, ax=ax, cmap='Reds', vmin=2000, vmax=3000)
fig.savefig('assets/calendar.png', bbox_inches='tight', dpi=75)

#####
# functions

def datetime_formatter(dt):
    # today = pd.to_datetime(date.today())
    today = pd.to_datetime(datetime.now().date())
    yesterday = pd.to_datetime(today - timedelta(days=1))
    # dt = pd.to_datetime(dt, format='%d%m%Y')
    dt = dt.date()
    # print(today, yesterday, dt)
    if dt == today:
        return 'Today'
    elif dt == yesterday:
        return 'Yesterday'
    else:
        return 'The before time'

def generate_food_table(dataframe, max_rows=10):
    dataframe = dataframe.reset_index()
    dataframe['Timestamp'] = dataframe['Timestamp'].apply(lambda x: datetime_formatter(x))
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def generate_calorie_graph(daily_calories):
        return dcc.Graph(
        id='Calories per Day',
        # config={'edits':{'legendPosition':}},
        figure={
            'data': [
                {'x': daily_calories.index, 'y': daily_calories['sum(calories)'], 'type': 'line', 'name': 'daily calories'},
                {'x': [daily_calories.index.min(), daily_calories.index.max()], 'y': [2000, 2000], 'type': 'line', 'name': u'You have eaten enough'},
            ],
            'layout': {
                'title': 'Calories per day'
                ,'showlegend':False
            }
        }
    )

# dash applications

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand="Demo",
    brand_href="#",
    sticky="top",
)
jumbotron = dbc.Jumbotron(
    [
        html.H1("Put down the fork!", className="display-1"),
        dcc.Markdown(
            "**Web app to track estimated calories consumed**",
            className="lead"
        ),
        html.Hr(className="my-2"),
        # html.P("Somedays I'm fat"),
        # html.P("Other days I'm thinner"),
        # html.P("Every day I count"),
        # html.P("A haiku by John Aiken"),
        # html.P('Opensource and available on github.'),
        # html.P(dbc.Button("github", color="primary"), className="lead"),
    ]
    , fluid=False
)
body = dbc.Container(
    [
        dbc.Row(
            [dbc.Col(
            [
        dcc.Markdown("*Somedays I'm fat*"),
        dcc.Markdown("*Other days I'm thinner*"),
        dcc.Markdown("*Every day I count*"),
        dcc.Markdown("A haiku"),
            ]
        )]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Recent food"),
                        generate_food_table(df.iloc[-10:])
                    ],
                    md=5,
                ),
                dbc.Col(
                    [
                        html.H2("Calories per day"),
                        # dcc.Graph(
                        #     figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                        # ),
                        generate_calorie_graph(daily_calories),
                    ]
                    , md=7
                ),0
            ]
        ),
        dbc.Row(
            [
                dbc.Col([html.Img(src='assets/calendar.png'),], md=12)
            ]
        )
    ],
    className="mt-4",
)
footer = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                [
                    html.P(''),
                    html.P('A web app by jm.'),
                ]
                ,md=12
            )
        ]
    )
)

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, external_stylesheets=['assets/bootstrap.css'])
server = app.server
app.title = 'Put down the fork!'

app.layout = html.Div([
    # navbar, 
    jumbotron, 
    body,
    footer
    ])

if __name__ == "__main__":
    app.run_server(debug=False)
