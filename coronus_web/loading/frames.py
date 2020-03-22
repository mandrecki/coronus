import pandas as pd

from .download import get_frames


cases_by_geolevel_type, geography = get_frames()


def get_cases(geolevel: str, cases_type: str):
    return cases_by_geolevel_type[geolevel][cases_type]


default_geolevel = "Country"
df_reco = get_cases(default_geolevel, "recovered")
df_conf = get_cases(default_geolevel, "confirmed")
df_dead = get_cases(default_geolevel, "dead")
df_active = get_cases(default_geolevel, "active")

df_aggregations = pd.concat([
    df_active.sum(axis=1).rename("Active cases"),
    df_conf.sum(axis=1).rename("Total cases"),
    df_dead.sum(axis=1).rename("Deaths"),
    df_reco.sum(axis=1).rename("Recoveries")
], axis=1)
df_perc_changes = df_aggregations.iloc[1:] / df_aggregations.iloc[:-1].values