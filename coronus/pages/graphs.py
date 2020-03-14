import pandas as pd
import numpy as np

import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq

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
    "Select countries": ["Italy", "Spain", "Korea, South", "United Kingdom"]
}

controls = [
    html.Div(
        [
            html.P([name + ":", dcc.Dropdown(id=name + "_dd", options=opts, multi=True, value=dd_def_vals[name])]) for name, opts in dd_options.items()
        ] +
        [
            daq.NumericInput(
                id="smoothing_growth",
                label="smoothing",
                min=1,
                max=10,
                value=2),
            dcc.Checklist(
                id="cases_checkbox",
                options=[
                    {'label': 'Log scale y', 'value': "log_y"},
                    {'label': 'Align growths', 'value': "align"},
                ],
                value=["align"],
                labelStyle={'display': 'inline-block'}),
        ],
        style={"width": "25%", "float": "right", },
        id="div_dd",
    )
]

plots = [
    html.H3("Active cases across regions"),
    dcc.Graph(id="cases_plot", style={"width": "75%", "display": "inline_block"}),
    html.H3("Daily growth of active cases"),
    html.P("All time series shifted so that maximum is at t=0. This is a moment when a country realises it needs to test more people. Previously hidden cases are uncovered which leads to an inflated growth estimate. "
           "After 15-20 days growth halts: new cases = cures + deaths. Then the virus starts to (very slowly) disappear from the population."),
    dcc.Graph(id="growth_plot", style={"width": "75%", "display": "inline_block"}),
    html.Br(),
]


layout = html.Div(
    controls + \
    plots
)

@dash_app.callback(
    [Output("cases_plot", "figure"), Output("growth_plot", "figure")],
    [Input(name + "_dd", "value") for name in dd_options.keys()] \
    + [Input("smoothing_growth", "value"), Input("cases_checkbox", "value")]
)
def make_plots(countries, smoothing, checkboxes):
    align_growths = True if "align" in checkboxes else False
    log_y = True if "log_y" in checkboxes else False

    active_cases = df_active.copy()
    if countries:
        active_cases = active_cases[countries]
    growths = cases_to_growths(active_cases, smoothing, align_max=align_growths, return_log=False)

    cases_fig = plot_interactive_df(active_cases[growths.columns], "Active cases", " ", name_sort=True)
    growths_fig = plot_interactive_df(growths, "Daily growth", " ", name_sort=True)

    cases_fig.update_layout(
        # legend_orientation="h",
        yaxis_type="log" if log_y else None,
    )
    growths_fig.update_layout(
        # legend_orientation="h",
        yaxis={"tickformat": '.1{}'.format("%")})

    return cases_fig, growths_fig