import plotly.express as px


def plot_interactive_df(df, ylabel, legend_label, name_sort=False):
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
    )
    fig.update_layout(margin={'t': 0})
    return fig