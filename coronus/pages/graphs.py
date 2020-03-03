import pandas as pd
import numpy as np

import plotly.express as px
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from app_def import dash_app

from ..loading.frames import df_active, df_conf, df_dead, df_reco


log_gr = np.log(df_active).reset_index().diff(1).replace([np.inf, -np.inf], np.nan)
new_cols = {}
for col in log_gr.iloc[:, 1:].columns:
    col_vals = log_gr.loc[log_gr[col].idxmax()-3:, col].reset_index(drop=True)
    new_cols.update({col: col_vals})
shifted_log_gr = pd.DataFrame(new_cols)
shifted_log_gr.index = shifted_log_gr.index - 3
shifted_log_gr.index.name = "days since peak growth"


def plot_interactive_df(df, ylabel, legend_label):
    order = df.max().sort_values(ascending=False).index
    df_plot = df[order.tolist()].reset_index()
    df_plot = df_plot.melt(id_vars=[df.index.name], value_name=ylabel, var_name=legend_label)
    fig = px.line(
        data_frame=df_plot,
        x=df.index.name,
        y=ylabel,
        color=legend_label,
    )
    return fig


plots = [
    html.Br(),
    html.H3("Active cases across regions"),
    dcc.Graph(figure=plot_interactive_df(df_active, "Cases", "region"),
              id="cases_plot", style={"width": "95%", "display": "inline_block"}),
    html.Br(),
    html.H3("Growth rate (log)"),
    html.H5("All timeseries shifted so that maximum is at t=0."),
    html.H5("After 2-3 weeks rate is 0 - new cases = cures + deaths - from that point onwards an epidemy starts petering out."),
    dcc.Graph(figure=plot_interactive_df(shifted_log_gr, "log growth", "region"),
              id="cases_plot", style={"width": "95%", "display": "inline_block"}),
    html.Br(),
]


layout = html.Div(
    plots
)

