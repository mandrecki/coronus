import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash
from app_def import dash_app
from coronus_web.pages import explore
from coronus_web.pages import we_predict
from coronus_web.pages import you_predict

server = dash_app.server
dash_app.title = 'Predict the virus'

header = html.Header(className='main-header', children=[
    html.Div(className='header-content', children=[
        html.H1(["Predict the virus"]),
        html.P("Explore the spread of COVID-19 and predict its impact", className='strapline')
    ]),
    html.Div(className='menu', children=[
        dcc.Link('Exploration', className='explore-link', href='/'),
        dcc.Link('Our models', className='predict-link', href='/our-models'),
        dcc.Link('Your predictions', className='predict-link', href='/your-predictions'),
    ])
])

footer = html.Div(id='footer', children=['♥♥♥deep-nearest-neighbours squooooood♥♥♥'])

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    header,
    html.Div(id='page-content'),
    footer
])


layout = html.Div([
    html.H1("(ง`_´)ง")
])


@dash_app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return explore.layout
    elif pathname == '/our-models':
        return we_predict.layout
    elif pathname == '/your-predictions':
        return you_predict.layout
    else:
        return '404'


if __name__ == '__main__':
    dash_app.run_server(debug=True)
