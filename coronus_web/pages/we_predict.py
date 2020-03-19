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
        plot("we_predict_plot", "Coming soon!",
             figure=plot_interactive_df(
                 df_aggregations[["Active cases", "Total cases"]], "Forecast", " ",
                 color_map={"Total cases": "lightgrey", "Active cases": "darkblue"}
             )
    ),
    # TODO: Should this have a heading?
    html.P([
        "Optimising...",
    ],
        className='intro', style={'whiteSpace': 'pre-wrap'}),
]

plots = [
]

layout = intro + plots
