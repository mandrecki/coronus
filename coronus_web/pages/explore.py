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


def table_digest():
    total_cases_now = df_aggregations["Total cases"].iloc[1:]
    cases_now = df_aggregations["Active cases"].iloc[1:]
    cases_yesterday = df_aggregations["Active cases"].iloc[:-1]
    new_cases = cases_now - cases_yesterday.values
    digest = pd.DataFrame({
        "Total cases": total_cases_now,
        "Active cases": cases_now,
        "Net new cases": new_cases,
        "Growth": (100 * new_cases / cases_yesterday.values)
    },
        index=total_cases_now.index
    )
    digest = digest.sort_index(ascending=False)
    digest_str = digest.applymap(lambda x: f"{x:,.0f}".format(int(x)))
    digest_str["Growth"] = digest["Growth"].map(lambda x: "{:.1f}%".format(x))
    digest_str = digest_str.reset_index()
    digest_str["Date"] = digest_str["Date"].map(lambda x: x.date())

    schemes = [
        px.colors.sequential.Greys_r[2:-1],
        px.colors.sequential.Greys_r[2:-1],
        px.colors.diverging.RdYlGn_r[2:-2],
        px.colors.diverging.RdYlGn_r[2:-2],
        px.colors.diverging.RdYlGn_r[2:-2],
    ]
    levels = [pd.qcut(digest.reset_index()[col],
                      len(schemes[i]),
                      labels=(range(len(schemes[i]))))
              for i, col in enumerate(digest.reset_index().columns)]
    fig = go.Figure(
        data=
        [
            go.Table(
                header=dict(values=list(digest_str.columns),
                line_color='white', fill_color='white',
                align='center',
                height=60,
                font=dict(color='dimgrey', size=30)),
                cells=dict(
                    values=[digest_str[col] for col in digest_str.columns],
                    fill_color=[np.array(schemes[i])[color] for i, color in enumerate(levels)],
                    align='center',
                    height=50,
                    font=dict(color='black', size=22)
                )
            )
        ]
    )
    fig.update_layout(
        height=500
    )
    graph = dcc.Graph(figure=fig)
    return graph


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
        html.Div(className='graph-container',
                 children=[table_digest()]),
        plot("welcome_plot", " ",
         figure=plot_interactive_df(df_aggregations[["Active cases", "Total cases"]], "Global COVID-19 cases", " ",
                                    color_map={"Total cases": "lightgrey", "Active cases": "darkblue"})
    ),
    # TODO: Should this have a heading?
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
        "Our research is divided into 3 sections: "
        "Exploration - visualise the spread of the contagion so far; "
        "Our models - see predictions made by our models; "
        "Your predictions - provide your own predictions and compare against the wisdom of the crowds.",
    ],
        className='intro', style={'whiteSpace': 'pre-wrap'}),
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
         "We can try to predict this pattern for countries in earlier stages of epidemy. "
         
         # TODO move to a separate g(r)ay paragraph
         
         "Hints: Logarithmic scale helps when comparing countries with very different scales of the contagion (e.g. Spain and Portugal). "
         "When plotted on a log scale, exponential trends are straight lines - the steepness of the line corresponds to the growth rate. "
         "You will notice that the curves corresponding to different regions are close to parallel (though not really straight)."
         "That is because the growth rate is similar across countries. This implies we can leverage past data for prognoses. "
         ),
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
    ),
    # TODO add explnation of the plot
    plot("growth_plot", "Daily growths",
         "Fill me!")
]

layout = intro + plots

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
