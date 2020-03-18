import plotly.express as px


def plot_interactive_df(df, ylabel, legend_label, name_sort=False, color_map={}):
    if name_sort:
        order = sorted(df.columns)
    else:
        order = df.max().sort_values(ascending=False).index.tolist()

    df_plot = df[order].reset_index()
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