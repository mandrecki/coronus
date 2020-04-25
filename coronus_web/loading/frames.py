import pandas as pd

from coronus_web.loading.download import get_flu_frames
from .download import get_frames
from .download import get_old_frames


# cases_by_geolevel, geography = get_frames()
cases_by_geolevel, geography = get_old_frames()


def get_cases(geolevel: str, cases_type: str) -> pd.DataFrame:
    """
    Returns a DataFrame with cases of specific type broken down by specific geographical level.
    This is fast - not downloading anything.
    """
    return cases_by_geolevel[geolevel][cases_type]


default_geolevel = "country"
df_reco = get_cases(default_geolevel, "recovered")
df_conf = get_cases(default_geolevel, "total")
df_dead = get_cases(default_geolevel, "deaths")
df_active = get_cases(default_geolevel, "active")
df_flu = get_flu_frames()

df_aggregations = pd.concat([
    df_active.sum(axis=1).rename("Active cases"),
    df_conf.sum(axis=1).rename("Total cases"),
    df_dead.sum(axis=1).rename("Deaths"),
    df_reco.sum(axis=1).rename("Recoveries")
], axis=1)
df_perc_changes = df_aggregations.iloc[1:] / df_aggregations.iloc[:-1].values