import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table

from dash.dependencies import Input, Output, State

from app_def import dash_app

from ..loading import df_active, df_conf, df_dead, df_reco, df_aggregations
from ..analysis.preprocessing import cases_to_growths
from ..plotting.plots import plot_interactive_df


def plot(graph_id, title, description=None, figure=None):
    if figure is not None:
        graph = dcc.Graph(id=graph_id, className='graph', figure=figure)
    else:
        graph = dcc.Graph(id=graph_id, className='graph')

    children = [
        html.H3(title),
        graph
    ]
    if description is not None:
        children.insert(1, html.P(description))

    return html.Div(className='graph-container', children=children)


intro = [
    # TODO: Should this have a heading?
    html.H3("What do you think will happen?"),
    html.P([
        "Every two weeks we will release a set of questions relating to COVID-19 and its impact. The goal is twofold.\n\n "
        "(1) We want to make your thoughts about this problem more concrete. Despite the uncertainty, current situation "
        "requires decisiviness and resolve. It is easy to make broad predictions, but those are rarely very useful. "
        "Push yourself to focus on the important detail. Realise after you were wrong and adapt. Maybe even make bets with your friends!\n\n "
        "(2) Your answers will contribute to \"wisdom of the crowds\". We will track how accurate community's opinions are "
        "and how they change over time and in response to particular government interventions. "
    ],
        className='intro', style={'whiteSpace': 'pre-wrap'}),
    html.A('Round 1 predictions',
           href='https://forms.gle/u2Brxj8REmRo4zoT8/',
           target="_blank")
]

layout = intro
