import numpy as np
import pandas as pd

import numpy as np

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C


def generate_gp_samples(df_aggregations):
    dates = pd.date_range(df_aggregations.index.min(), "2020-05-01", name="Date")

    data = np.log(df_aggregations.reset_index()["Active cases"]).dropna()
    X = np.atleast_2d(data.index).T
    y = np.atleast_2d(data.values).T - data.mean()

    kernel = C(1.0, (1e-3, 1e3)) * RBF(1, (1e-2, 1e2))
    gp = GaussianProcessRegressor(kernel=kernel, alpha=0.05,
                                  n_restarts_optimizer=10)
    gp.fit(X, y)

    x = np.atleast_2d(np.arange(0, len(dates))).T
    lines = {i: sample.flatten() + data.mean() for i, sample in enumerate(gp.sample_y(x, 35).T)}
    forecast = pd.DataFrame(
        lines,
        index=pd.Series(x.flatten(), name="Days")
    )
    forecast["observations"] = data
    forecast = np.exp(forecast)
    forecast = forecast.drop(columns=forecast.columns[(forecast.max() > 0.85 * 1e8)])
    forecast.index = dates
    return forecast


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
