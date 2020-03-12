import numpy as np
import pandas as pd


def cases_to_growths(df_active, smoothing, return_log=False):
    filtered = df_active.copy()
    # filtered[filtered<20] = np.nan

    if smoothing > 1:
        filtered = filtered.rolling(smoothing, min_periods=1).apply(lambda x: x.sum()/x.notna().sum(), raw=False)

    log_gr = np.log(filtered).reset_index().diff(1).replace([np.inf, -np.inf], np.nan)
    log_gr = log_gr.dropna(axis="columns", how="all")
    # if smoothing > 0:
    #     log_gr = log_gr.rolling(smoothing, min_periods=1).apply(lambda x: x.sum()/x.notna().sum(), raw=False)

    new_cols = {}
    for col in log_gr.iloc[:, 1:].columns:
        col_vals = log_gr.loc[log_gr[col].idxmax() - 4:, col].reset_index(drop=True)
        if len(col_vals) > 5:
            new_cols.update({col: col_vals})
    shifted_log_gr = pd.DataFrame(new_cols)
    shifted_log_gr.index = shifted_log_gr.index - 4
    shifted_log_gr.index.name = "days since peak growth"

    if return_log:
        return shifted_log_gr
    else:
        return np.exp(shifted_log_gr) - 1