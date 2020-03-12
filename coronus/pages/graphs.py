import pandas as pd
import numpy as np

import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

from app_def import dash_app

from ..loading.frames import df_active, df_conf, df_dead, df_reco
from ..analysis.preprocessing import cases_to_growths
from ..plotting.plots import plot_interactive_df

# controls for the graph
dd_options = {
    "Select countries": [dict(label=x, value=x) for x in df_active.columns if df_conf[x].max() > 20],
}
dd_def_vals = {
    "Select countries": ["Italy", "Republic of Korea", "UK", "Germany", "Spain"]
}

controls = [
    html.Div(
        # [html.Button("", id="dummy_button", hidden=True)]
        # +
        [
            html.P([name + ":", dcc.Dropdown(id=name + "_dd", options=opts, multi=True, value=dd_def_vals[name])]) for name, opts in dd_options.items()
        ],
        style={"width": "25%", "float": "right", },
        id="div_dd",
    )
]
    # [dcc.Checklist(
    #             id="cases_checkbox",
    #             options=[
    #                 {'label': 'Log scale x', 'value': "log_x"},
    #                 {'label': 'Log scale y', 'value': "log_y"},
    #             ],
    #             value=[],
    #             labelStyle={'display': 'inline-block'})]
    # +
    # [

plots = [

    html.H3("Active cases across regions"),
    dcc.Graph(id="cases_plot", style={"width": "75%", "display": "inline_block"}),
    html.H3("Growth rate"),
    html.P("All timeseries shifted so that maximum is at t=0. After 2-3 weeks rate is 1 - new cases = cures + deaths - from that point onwards an epidemy starts petering out."),
    dcc.Graph(id="growth_plot", style={"width": "75%", "display": "inline_block"}),
    html.Br(),
]


layout = html.Div(
    controls + \
    plots
)

@dash_app.callback(
    [Output("cases_plot", "figure"), Output("growth_plot", "figure")],
    [Input(name + "_dd", "value") for name in dd_options.keys()]
)
def make_plots(countries):
    active_cases = df_active.copy()
    if countries:
        active_cases = active_cases[countries]
    growths = cases_to_growths(active_cases, return_log=False)

    cases_fig = plot_interactive_df(active_cases[growths.columns], "cases", " ", name_sort=True)
    growths_fig = plot_interactive_df(growths, "growth", " ", name_sort=True)

    cases_fig.update_layout(legend_orientation="h")
    growths_fig.update_layout(legend_orientation="h",
                              yaxis={"tickformat": '.1{}'.format("%")})

    return cases_fig, growths_fig