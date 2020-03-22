import datetime

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table
import stringcase

from dash.dependencies import Input, Output, State

from app_def import dash_app

from ..loading.frames import df_active, df_conf, df_dead, df_reco, df_aggregations, df_perc_changes, get_cases
from ..analysis.preprocessing import cases_to_growths
from ..plotting.plots import plot_interactive_df
from ..loading.download import GEO_LEVELS

digest_color_scheme = px.colors.diverging.RdYlGn_r[2:-2]


def get_quantiles(df, col):
    return pd.qcut(df[col], len(digest_color_scheme), labels=range(len(digest_color_scheme)))


df_aggregations_quantiles = {col: get_quantiles(df_aggregations, col) for col in df_aggregations}
df_perc_changes_quantiles = {col: get_quantiles(df_perc_changes, col) for col in df_perc_changes}


def digest_for(aggregation):
    today = df_aggregations[aggregation][-1]
    today_clr = digest_color_scheme[df_aggregations_quantiles[aggregation][-1]] if aggregation != 'Total cases' else None
    yesterday = df_aggregations[aggregation][-2]
    perc_change = df_perc_changes[aggregation][-1] * 100 - 100
    perc_change_clr = digest_color_scheme[df_perc_changes_quantiles[aggregation][-1]]
    return html.P([
        f"{aggregation}: ",
        html.Span(f"{today:,.0f}", className='today', style={'color': today_clr}),
        ' ',
        html.Span([
            '(',
            html.Span(f"{perc_change:+.0f}%", className='percent-change', style={'color': perc_change_clr}),
            f" from {yesterday:,.0f})"
        ], className='yesterday')
    ], className=stringcase.spinalcase(aggregation))


def table_digest():
    latest_date = df_aggregations.index[-1]
    return html.Div([
        html.H1([
            "Latest stats ",
            html.Span("({})".format(latest_date.strftime('%d %b %Y')))
        ]),
        digest_for('Active cases'),
        digest_for('Total cases')
    ], className='stats-digest')


def plot(graph_id, title, description=None, figure=None):
    if figure is not None:
        graph = dcc.Graph(id=graph_id, className='graph', figure=figure)
    else:
        graph = dcc.Graph(id=graph_id, className='graph')




    children = [
        html.H3(title),
        dcc.Loading(graph, style={"height": 500})
    ]
    if description is not None:
        children.insert(1, dcc.Markdown(description))

    return html.Div(className='graph-container', children=children)

# controls for the graph
dd_options = {
    "Select countries": [dict(label=x, value=x) for x in df_active.columns if df_conf[x].max() > 20],
}
dd_def_vals = {
    "Select countries": ["Italy", "Spain", "Korea, South", "United Kingdom"]
}

intro = [
        table_digest(),
        plot("welcome_plot", " ",
         figure=plot_interactive_df(df_aggregations[["Active cases", "Total cases"]], "Global COVID-19 cases", " ",
                                    color_map={"Total cases": "lightgrey", "Active cases": "darkblue"})
    ),
    # TODO: Should this have a heading?
    html.Div([
        # html.H1("Why predict?"),
        html.H1("Why we predict?"),
        # html.H1("Our mission?"),
        html.P([
            "We use machine learning methodology to forecast the future extent and impact of the ongoing pandemy. "
            "World's governments are now making crucial decisions that will affect nearly everybody on the planet. "
            "How much effort should be placed on preventing further spread? To what extent should we be willing to sacrifice stability of our economies? "
            "The challenge of balancing the trade-offs is excarbated by the uncertainty. \n\n"
            "Some nations were unlucky to experience COVID-19 early, when little was known. "
            "But those who follow, should learn from their successes and mistakes. "
            "As data scientists we feel obligated to drive the uncertainty down and aggregate whatever insights may be valuable for the decision-makers. "
            "Our research is divided into three sections: "
            "Exploration - visualise the spread of the contagion so far; "
            "Our models - see predictions made by our models; "
            "Your predictions - provide your own predictions and compare against the wisdom of the crowds.",
        ]),
    ], className='intro')
]

plots = [
    # TODO make legends transparent
    plot("cases_plot", 'Focus on the active cases',
         "How many people will get infected in the next month depends on how many people carry the virus now, not in January. "
         "That is why we focus our attention on the number of active cases and its evolution (rather than the total number of cases to date). "
         "By considering active cases you will notice that the contagion is on the verge of receding in some countries (South Korea or Singapore). "
         "China is on a promising path towards recovery. "
         "Using the dropdown below you can compare how quickly the virus has spread through countries. "
         "For countries with many weeks of history, we observe initial exponential growth that ultimately plateaus. "
         "We can try to predict this pattern for countries in earlier stages of epidemy. \n\n "
         
         # TODO move to a separate g(r)ay paragraph
         
         "Hints: Logarithmic scale helps when comparing countries with very different scales of the contagion (e.g. Spain and Portugal). "
         "When plotted on a log scale, exponential trends are straight lines - the steepness of the line corresponds to the growth rate. "
         "You will notice that the curves corresponding to different regions are close to parallel (though not really straight)."
         "That is because the growth rate is similar across countries. This implies we can leverage past data for prognoses. "
         ),
    html.Div(
        [
            html.Div([
                html.Span(["Select regions:"], className='value-select-label'),
                dcc.Dropdown(id="regions_dd", multi=True)
            ], className='value-select input-container')
        ] +
        [
            dcc.Checklist(
                id="cases_checkbox",
                className="input-container",
                options=[
                    {'label': 'Log scale y', 'value': "log_y"},
                    {'label': 'Align growths', 'value': "align"},
                ],
                value=["align"],
                persistence=True
            ),
            dcc.RadioItems(
                id="breakdown_radio",
                options=[{"label": geo_level, "value": geo_level} for geo_level in GEO_LEVELS],
                value="Country",
                persistence=True,

            ),
            daq.NumericInput(
                id="smoothing_growth",
                className="input-container",
                label="Smoothing",
                labelPosition="top",
                min=1,
                max=10,
                value=2,
            )
        ],
        id="div_dd"
    ),
    plot("growth_plot", "Monitor growth or decay",
         "An epidemy is an exponential phenomenom. Everyday the number of active cases is multiplied by a factor. "
         "If the virus is winning, the number is greater than 1. If we are winning, the number is less than 1. "
         "In this plot, we present a daily percentage change in confirmed active cases. "
         "The horizontal axis indicates the number of days since the ignition of the epidemy in a given region. "
         "Initially, most areas see extremely high daily growths. The number of cases can increase by more than 100%. "
         "This doesn't necessarily mean that the virus is spreading that quickly. In most cases, this number reflects "
         "the fact that countries test their citizens more diligently. \n\n"
         
         "Over time the growth stabilises and gradually decays. Ultimately, it goes below 0% (see China) meaning that the virus recedes.  "
         "This graph has the regions aligned on their initial outbreak - you can use that to predict future growths in countries "
         "that have seen the outbreak only recently. Countries that are dealing with the virus for many weeks already can be "
         "a good reference. \n\n"
         ""
         "Hint: you can tick/untick *align growths* to plot growths against days since outbreak or date. In the second case "
         "the growth will match to the plot above. "
         "")
]
layout = intro + plots


@dash_app.callback(
    [Output("regions_dd", "options"), Output("regions_dd", "persistence")],
    [Input("breakdown_radio", "value")]
)
def make_dropdown(geo_level):
    df_active = get_cases(geo_level, "active")
    df_conf = get_cases(geo_level, "confirmed")
    dd_options = [dict(label=x, value=x) for x in df_active.columns if df_conf[x].max() > 20]
    return [dd_options, geo_level]

@dash_app.callback(
    [Output("cases_plot", "figure"), Output("growth_plot", "figure")],
    [Input("regions_dd", "value")] \
    + [Input("smoothing_growth", "value"), Input("cases_checkbox", "value")],
    [State("breakdown_radio", "value")]
)
def make_plots(regions, smoothing, checkboxes, geo_level):
    align_growths = True if "align" in checkboxes else False
    log_y = True if "log_y" in checkboxes else False

    active_cases = get_cases(geo_level, "active")
    if regions:
        active_cases = active_cases[regions]
    else:
        # hard limit to 10 regions
        active_cases = active_cases.iloc[:, :10]

    growths = cases_to_growths(active_cases, smoothing, align_max=align_growths, return_log=False)

    cases_fig = plot_interactive_df(active_cases[growths.columns], "Active cases", " ", name_sort=True)
    growths_fig = plot_interactive_df(growths, "Daily growth", " ", name_sort=True)

    cases_fig.update_layout(
        yaxis_type="log" if log_y else None,
        legend={"bgcolor": "rgba(0,0,0,0)"},
    )
    growths_fig.update_layout(
        yaxis={"tickformat": '.1{}'.format("%")},
        legend={"bgcolor": "rgba(0,0,0,0)"}
    )

    return cases_fig, growths_fig
