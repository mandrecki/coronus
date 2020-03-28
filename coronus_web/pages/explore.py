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

from ..loading.frames import geography, df_aggregations, df_perc_changes, get_cases
from ..analysis.preprocessing import cases_to_growths
from ..plotting.plots import plot_interactive_df, human_format
from ..loading.download import GEO_LEVELS, CASE_TYPES

digest_color_scheme = px.colors.diverging.RdYlGn_r[1:-1]


def get_quantiles(df, col):
    return pd.qcut(df[col]+0.0001*np.random.randn(len(df[col])), len(digest_color_scheme), labels=range(len(digest_color_scheme)))


df_aggregations_quantiles = {col: get_quantiles(df_aggregations, col) for col in df_aggregations}
df_perc_changes_quantiles = {col: get_quantiles(df_perc_changes, col) for col in df_perc_changes}


def digest_for(aggregation):
    today = df_aggregations[aggregation][-1]
    today_clr = digest_color_scheme[df_aggregations_quantiles[aggregation][-1]] if aggregation != 'Total cases' else None
    yesterday = df_aggregations[aggregation][-2]
    perc_change = df_perc_changes[aggregation][-1] * 100 - 100
    perc_change_clr = digest_color_scheme[df_perc_changes_quantiles[aggregation][-1]]
    # if active cases are not available
    #     today_clr = "rgba(100,100,100,100)"
    #     perc_change_clr = "rgba(100,100,100,100)"
    #     today = 0
    #     yesterday = 0
    #     perc_change = np.nan

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
        html.H2([
            "Daily stats ",
            html.Span("({})".format(latest_date.strftime('%d %b %Y')))
        ]),
        digest_for('Active cases'),
        digest_for('Total cases')
    ], className='stats-digest')


def make_map_figure():
    # https://plot.ly/python/v3/animations/
    geo_level = "state"
    active = get_cases(geo_level, "total")

    df_plot = active.unstack()
    df_plot = pd.concat([
        df_plot.rename("cases"),
        np.log10(df_plot).rename("log10(cases)")
    ], axis=1).replace(-np.inf, np.nan).fillna(0).reset_index()
    df_plot.date = df_plot.date.map(lambda x: str(x.date()))
    df_plot = df_plot.merge(geography[["state", "lat", "long", "continent", "country"]], on=geo_level, how="inner")

    fig = px.scatter_mapbox(
        data_frame=df_plot,
        lat="lat", lon="long",
        # size="cases",
        size="log10(cases)",
        # color="continent",
        color="log10(cases)",
        hover_name=geo_level,
        hover_data=["cases", "country"],
        animation_frame="date",
        animation_group=geo_level,
        color_continuous_scale="sunset",
        height=750,
    )
    ticks = np.arange(0, 10)
    fig.update_layout(coloraxis_colorbar=dict(
        title="Total cases",
        tickvals=ticks,
        ticktext=list(map(human_format,  10**ticks))
    ))
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=1.25, mapbox_center={"lat": 28.0, "lon": 15.0})
    fig.update_layout(margin={"r": 20, "t": 0, "l": 20, "b": 0})

    return fig


def plot(graph_id, title, description=None, figure=None):
    if figure is not None:
        graph = dcc.Graph(id=graph_id, className='graph', figure=figure)
    else:
        graph = dcc.Graph(id=graph_id, className='graph')

    children = [
        html.H2(title),
        dcc.Loading(graph, style={"height": 600})
    ]
    if description is not None:
        children.insert(1, dcc.Markdown(description))

    return html.Div(className='graph-container', children=children)


intro = [
    table_digest(),
    plot("welcome_plot", " ",
         figure=plot_interactive_df(df_aggregations[["Active cases", "Total cases", "Deaths", "Recoveries"]], "Global COVID-19 cases", " ",
                                    color_map={"Total cases": "lightgrey", "Active cases": "darkblue", "Deaths": "orangered", "Recoveries": "green"})
    ),
    html.Div([
        html.H2("Why we predict?"),
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
         
         # TODO move to a separate gray paragraph
         
         "Hints: Logarithmic scale helps when comparing countries with very different scales of the contagion (e.g. Spain and Portugal). "
         "When plotted on a log scale, exponential trends are straight lines - the steepness of the line corresponds to the growth rate. "
         "You will notice that the curves corresponding to different regions are close to parallel (though not really straight)."
         "That is because the growth rate is similar across countries. This implies we can leverage past data for prognoses. "
         ),
    html.Div(
        [
            html.Div([
                html.Span(["Case type:"], className='value-select-label'),
                dcc.RadioItems(
                    id="case_type_radio",
                    options=[{"label": case_type.capitalize(), "value": case_type} for case_type in CASE_TYPES],
                    value="active",
                    persistence=True,
                ),
            ], className='value-select input-container'),
            html.Div([
                html.Span(["Breakdown by:"], className='value-select-label'),
                dcc.RadioItems(
                    id="breakdown_radio",
                    options=[{"label": geo_level.capitalize(), "value": geo_level} for geo_level in GEO_LEVELS[1:]],
                    value="country",
                    persistence=True,
                ),
            ], className='value-select input-container'),
            html.Div([
                html.Span(["Select regions:"], className='value-select-label'),
                dcc.Dropdown(id="regions_dd", multi=True)
            ], className='value-select input-container input-container-long'),
            html.Div([
                html.P(["Advanced options:"]),
                html.Div([
                    dcc.Checklist(
                        id="cases_checkbox",
                        options=[
                            {'label': 'Log scale y', 'value': "log_y"},
                            {'label': 'Align growths', 'value': "align"},
                        ],
                        value=["align"],
                        persistence=True
                    ),
                    daq.NumericInput(
                        id="smoothing_growth",
                        label="Smoothing",
                        min=1,
                        max=10,
                        value=2,
                    )
                ], className='input-container-line')
            ], className='input-container input-container-long')
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
         ""),
    plot("map_plot", "How has the virus spread?", figure=make_map_figure())

]
layout = intro + plots

@dash_app.callback(
    [Output("regions_dd", "options"), Output("regions_dd", "persistence"),  Output("regions_dd", "value")],
    [Input("breakdown_radio", "value")]
)
def make_dropdown(geo_level):
    dd_options = [dict(label=x, value=x) for x in sorted(geography[geo_level].dropna().unique())]
    DEFAULT_REGIONS = {
        "state": ["Ontario"],
        "country": ["United Kingdom", "Italy", "US", "China", "Spain"],
        "continent": ["Asia", "Africa", "Europe", "Oceania", "North America", "South America"],
        "global": ["global"],
    }
    regions = DEFAULT_REGIONS[geo_level]

    return [dd_options, geo_level, regions]

@dash_app.callback(
    [Output("cases_plot", "figure"), Output("growth_plot", "figure")],
    [Input("regions_dd", "value"), Input("smoothing_growth", "value"), Input("cases_checkbox", "value"), Input("case_type_radio", "value")],
    [State("breakdown_radio", "value")]
)
def make_plots(regions, smoothing, checkboxes, case_type, geo_level):
    align_growths = True if "align" in checkboxes else False
    log_y = True if "log_y" in checkboxes else False

    cases = get_cases(geo_level, case_type)
    if regions:
        cases = cases[regions]
    else:
        # hard limit to 10 regions
        cases = cases.iloc[:, :10]

    growths = cases_to_growths(cases, smoothing, align_max=align_growths, return_log=False)
    cases_fig = plot_interactive_df(cases, "{} cases".format(case_type.capitalize()), " ")

    if len(growths) > 0:
        growths_fig = plot_interactive_df(growths, "Daily {} case growth".format(case_type), " ")

        cases_fig.update_layout(
            yaxis_type="log" if log_y else None,
        )
        growths_fig.update_layout(
            yaxis={"tickformat": '.1{}'.format("%")},
        )

    else:
        growths_fig = {}

    return cases_fig, growths_fig


