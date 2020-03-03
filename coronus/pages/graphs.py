import pandas as pd
import numpy as np

from six.moves.urllib.parse import quote

import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from coronus.app import dash_app

from coronus.coronus.loading.frames import df_active, df_conf, df_dead, df_reco


def plot_interactive_df(df):
    order = df.max().sort_values(ascending=False).index
    df_plot = df[order.tolist()].reset_index()
    df_plot = df_plot.melt(id_vars=[df.index.name], value_name="Cases", var_name="region")
    fig = px.line(
        data_frame=df_plot,
        x=df.index.name,
        y="Cases",
        color="region",
    )
    return fig


plots = [
    html.Br(),
    html.H3("Cases plot"),
    dcc.Graph(figure=plot_interactive_df(df_active),
              id="cases_plot", style={"width": "95%", "display": "inline_block"}),
    html.Br(),
]


layout = html.Div(
    plots
)

