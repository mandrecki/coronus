import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash
from coronus.pages import graphs


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
dash_app.config.suppress_callback_exceptions = True


dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Link('[Home]', href='/'),
    dcc.Link('[Graphs]', href='/graphs'),
    html.Br(),
    html.Div(id='page-content'),
])


layout = html.Div([
    html.H1("(ง`_´)ง")
])

@dash_app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return layout
    elif pathname == '/graphs':
        return graphs.layout
    else:
        return '404'


if __name__ == '__main__':
    dash_app.run_server(debug=False)
