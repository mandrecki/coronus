import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash
from app_def import dash_app
from coronus.pages import graphs

server = dash_app.server

menu = html.Div([
        dcc.Link('[Graphs]', href='/'),
        # dcc.Link('[Graphs]', href='/graphs'),
    ],
    style={
        'marginBottom': 50, 'marginTop': 25,
        "width": "80%",
    })

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    menu,
    html.Div(id='page-content', style={
        'marginBottom': 50, 'marginTop': 25,
        "width": "80%",
    }),
])



layout = html.Div([
    html.H1("(ง`_´)ง")
])

@dash_app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return graphs.layout
    elif pathname == '/graphs':
        return graphs.layout
    else:
        return '404'


if __name__ == '__main__':
    dash_app.run_server(debug=True)
