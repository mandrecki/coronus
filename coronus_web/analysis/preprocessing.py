import numpy as np
import pandas as pd


def cases_to_growths(df_active, smoothing, align_max=True, return_log=False):
    active = df_active.copy()

    if smoothing > 1:
        active = active.rolling(smoothing, min_periods=1).apply(lambda x: x.sum()/x.notna().sum(), raw=False)

    log_gr = np.log(active).diff(1).replace([np.inf, -np.inf], np.nan)
    log_gr = log_gr.dropna(axis="columns", how="all")

    if align_max:
        log_gr = log_gr.reset_index()
        new_cols = {}
        for col in log_gr.iloc[:, 1:].columns:
            col_vals = log_gr.loc[log_gr[col].idxmax() - 4:, col].reset_index(drop=True)
            if len(col_vals) > 5:
                new_cols.update({col: col_vals})
        log_gr = pd.DataFrame(new_cols)
        log_gr.index = log_gr.index - 4
        log_gr.index.name = "Days since peak growth"

    if return_log:
        return log_gr
    else:
        return np.exp(log_gr) - 1