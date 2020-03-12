import numpy as np
import pandas as pd


def cases_to_growths(df_active, return_log=False):
    filtered = df_active.copy()
    filtered[filtered<20] = np.nan
    log_gr = np.log(filtered).reset_index().diff(1).replace([np.inf, -np.inf], np.nan)
    log_gr = log_gr.dropna(axis="columns", how="all")
    new_cols = {}
    for col in log_gr.iloc[:, 1:].columns:
        col_vals = log_gr.loc[log_gr[col].idxmax() - 4:, col].reset_index(drop=True)
        new_cols.update({col: col_vals})
    shifted_log_gr = pd.DataFrame(new_cols)
    shifted_log_gr.index = shifted_log_gr.index - 4
    shifted_log_gr.index.name = "days since peak growth"
    if return_log:
        return shifted_log_gr
    else:
        return np.exp(shifted_log_gr) - 1