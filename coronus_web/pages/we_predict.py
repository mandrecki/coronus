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
from ..analysis.preprocessing import generate_gp_samples
from ..plotting.plots import plot_interactive_df


def generate_gp_figure():
    forecast = generate_gp_samples(df_aggregations)
    cmap = {col: "lightgrey" for col in forecast.columns}
    cmap["observations"] = "green"
    fig = plot_interactive_df(forecast, "Global active cases", " ", color_map=cmap)
    fig = fig.update_layout(
        showlegend=False,
        yaxis_type="log",
    )
    return fig


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
             figure=generate_gp_figure()
             ),
    # TODO: Should this have a heading?
    html.P([
        "Optimising... Do not rely on these predictions. Learning in progress...",
    ],
        className='intro', style={'whiteSpace': 'pre-wrap'}),
]

plots = [
]

layout = intro + plots
