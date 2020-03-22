
import numpy as np
import pandas as pd

urls = dict(
    confirmed="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",
    recovered="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv",
    dead="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv",
)

GEO_LEVELS = [
    "State",
    "Country",
    # "Continent"
    "Global"
]


def get_continents():
    filename = "../../data/country_to_continent.csv"
    df = pd.read_csv(filename, encoding = "iso-8859-1")
    return df


def append_continents(cases, continents):
    df_cases_enriched = cases.merge(continents,
                                       on='Country/Region',
                                       how="left")
    return df_cases_enriched

def get_raw_df(url):
    #     s = requests.get(url).content
    #     df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df = pd.read_csv(url)
    df = df.rename(columns={
        "Province/State": "State",
        "Country/Region": "Country",
    })
    df["Global"] = "Global"
    df.loc[df["State"].isna(), "State"] = df.loc[df["State"].isna(), "Country"]
    return df


def to_spacetime(df, geolevel: str):
    drop_cols = GEO_LEVELS + ["Lat", "Long"]
    drop_cols.remove(geolevel)
    df = df.drop(columns=drop_cols)
    df = df.groupby(geolevel).sum()
    df = df.T
    df.index.name = "Date"
    df.index = pd.to_datetime(df.index)
    return df


def calculate_active(spacetime_dict):
    active = spacetime_dict["confirmed"] - spacetime_dict["recovered"] - spacetime_dict["dead"]
    return active.replace(0, np.nan)


def get_frames():
    raw = {count_type: get_raw_df(url) for count_type, url in urls.items()}



    geography = raw["confirmed"][["State", "Country", "Global",  "Lat", "Long"]]
    cases_by_geolevel = dict()
    for geolevel in GEO_LEVELS:
        spacetime = {count_type: to_spacetime(raw[count_type], geolevel=geolevel) for count_type in raw.keys()}
        spacetime["active"] = calculate_active(spacetime)
        cases_by_geolevel[geolevel] = spacetime

    return cases_by_geolevel, geography
