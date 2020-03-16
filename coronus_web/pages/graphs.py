import pandas as pd
import numpy as np

import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq

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

# controls for the graph
dd_options = {
    "Select countries": [dict(label=x, value=x) for x in df_active.columns if df_conf[x].max() > 20],
}
dd_def_vals = {
    "Select countries": ["Italy", "Spain", "Korea, South", "United Kingdom"]
}

intro = [
    plot("welcome_plot", "Global cases over time",
         figure=plot_interactive_df(df_aggregations[["Active cases", "Total cases"]], "  ", " ",
                                    color_map={"Total cases": "lightgrey", "Active cases": "darkblue"})
    ),
    html.P([
        "We offer forecasts of the future extent of the pandemy and its impacts to aid the world in finding the best responses. "
        "Governments are now making crucial decisions that will affect nearly everybody on the planet. "
        "How much effort should be placed on preventing further spread? To what extent should we be willing to sacrifice stability of our economies? "
        "The challenge of balancing the trade-offs is excarbated by the uncertainty. \n\n"
        "Some nations were unlucky to experience Covid-19 early, when little was known. "
        "But those who follow, should learn from their successes and mistakes. "
        "As data scientists we feel obligated to drive the uncertainty down and aggregate whatever insights may be valuable for the decision-makers. "
        "This site presents: "
        "(1) progression of the contagion so far, "
        "(2) predictive models developed using machine learning methodology, "
        "(3) aggregation of predictions by its users (the wisdom of crowds).",
    ],
        className='intro', style={'whiteSpace': 'pre-wrap'}),
]

controls = [
    html.Div(
        [
            html.Div([
                html.Span([name + ":"], className='value-select-label'),
                dcc.Dropdown(id=name + "_dd", options=opts, multi=True, value=dd_def_vals[name])
            ], className='value-select input-container')
            for name, opts in dd_options.items()
        ] +
        [
            dcc.Checklist(
                id="cases_checkbox",
                className="input-container",
                options=[
                    {'label': 'Log scale y', 'value': "log_y"},
                    {'label': 'Align growths', 'value': "align"},
                ],
                value=["align"]),
            daq.NumericInput(
                id="smoothing_growth",
                className="input-container",
                label="Smoothing",
                labelPosition="top",
                min=1,
                max=10,
                value=2)
        ],
        id="div_dd"
    )
]

plots = [

    plot('cases_plot', 'Active cases across regions',
         "How many people will get infected in the next month depends on how many people carry the virus now, not in January. "
         "That is why we focus our attention on the number of active cases and its evolution (rather than number of cases to date). "
         "By considering active cases you will notice that the contagion is on the verge of receding in some countries (South Korea or Singapore). "
         "China is on a promising path towards recovery. "
         "Using the dropdown below you can compare how quickly the virus has spread through countries. "
         "For countries with many weeks of history, we observe initial exponential growth that ultimately plateaus. "
         "We can try to predict this pattern for countries in earlier stages of epidemy. "
         "Hint: Logarithmic scale helps when comparing countries with very different scales of the contagion (e.g. Spain and Portugal). "
         ),
    plot('growth_plot', 'Daily growth of active cases',
         "All time series shifted so that maximum is at t = 0. This is a moment when a  country realises it needs "
         "to test more people. Previously hidden cases are uncovered which leads to an inflated growth estimate. "
         "After 15-20 days growth halts: new cases = cures + deaths. Then the virus starts to (very slowly) disappear "
         "from the population.")
]

layout = intro + controls + plots

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
