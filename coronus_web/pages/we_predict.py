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
from coronus_web.pages.explore import plot

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


intro = [
        plot("we_predict_plot", "Our predictions - coming soon",
             description=(
                 "We are currently working on models that predict the spread of COVID-19. "
                 "As the models are developed, we will update this page with information about them and their predictions.\n\n"
                 "You can also provide predictions of your own on the [You predict](/you-predict) page. "
             ),
             figure=generate_gp_figure()
        )
]

plots = [
]

layout = intro + plots
