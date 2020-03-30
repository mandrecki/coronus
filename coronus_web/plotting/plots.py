import plotly.express as px
import pandas as pd

def plot_interactive_df(df: pd.DataFrame, ylabel: str = "value", title: str = "", sort_by: str = "", color_map: dict = None):
    df = df.copy()

    if color_map is None:
        color_map = {}

    if sort_by:
        if sort_by == "name":
            order = sorted(df.columns)
            df_plot = df[order]
        elif sort_by == "max_value":
            order = df.max().sort_values(ascending=False).index.tolist()
            df_plot = df[order]
        else:
            raise ValueError("Cannot sort by {}".format(sort_by))
    else:
        df_plot = df

    if df.index.name is None:
        df.index.name = "index"

    df_plot = df_plot.reset_index()

    legend_label = "   "
    df_plot = df_plot.melt(id_vars=[df.index.name], value_name=ylabel, var_name=legend_label)
    fig = px.line(
        data_frame=df_plot,
        x=df.index.name,
        y=ylabel,
        color=legend_label,
        color_discrete_map=color_map,
        template="plotly_white",
        height=600,
        title=title,
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        yaxis={
            "side": "right",
            'fixedrange': True
        },
        xaxis={
            'fixedrange': True
        },
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "x": 0,
            "y": 1,
        },
        font={
            "size": 16
        },
    )

    return fig


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def old_plot_interactive_df(df, ylabel, legend_label, sort_by=None, color_map={}):
    if sort_by is None:
        df_plot = df.reset_index()
    elif sort_by == "name":
        order = sorted(df.columns)
        df_plot = df[order].reset_index()
    elif sort_by == "max_value":
        order = df.max().sort_values(ascending=False).index.tolist()
        df_plot = df[order].reset_index()
    else:
        raise ValueError

    df_plot = df_plot.melt(id_vars=[df.index.name], value_name=ylabel, var_name=legend_label)
    fig = px.line(
        data_frame=df_plot,
        x=df.index.name,
        y=ylabel,
        color=legend_label,
        color_discrete_map=color_map,
        template="plotly_white",
        height=600,
    )
    fig.update_layout(
        margin={'t': 32},
        yaxis={
            "side": "right",
            'fixedrange': True
        },
        xaxis={
            'fixedrange': True
        },
        legend={
            "x": 0,
            "y": 1,
        },
        font={
            "size": 16
        },
    )

    return fig

