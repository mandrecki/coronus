import pandas as pd
import numpy as np
import io
import requests

def load_region_values(url):
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df = df.drop(columns=["Lat", "Long"])
    df.loc[df["Province/State"].isna(), "Province/State"] = df.loc[df["Province/State"].isna(), "Country/Region"]
    df = df.drop(columns=["Country/Region"])
    df = df.set_index("Province/State").T
    df = df.reset_index(drop=False).reset_index(drop=True)
    df = df.rename(columns={"index": "Date"})
    df.Date = pd.to_datetime(df.Date)
    df = df.set_index("Date")
    return df

def load_country_values(url):
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    df = df.drop(columns=["Lat", "Long", "Province/State"])
    df = df.groupby("Country/Region").sum()
    df = df.T
    df = df.reset_index(drop=False).reset_index(drop=True)
    df = df.rename(columns={"index": "Date"})
    df.Date = pd.to_datetime(df.Date)
    df = df.set_index("Date")
    return df

url_reco = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"
url_dead = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
url_conf = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
df_reco = load_country_values(url_reco)
df_conf = load_country_values(url_conf)
df_dead = load_country_values(url_dead)
df_active = df_conf - df_reco - df_dead
df_active = df_active.replace(0, np.nan)
df_aggregations = pd.concat([
    df_active.sum(axis=1).rename("Active cases"),
    df_conf.sum(axis=1).rename("Total cases"),
    df_dead.sum(axis=1).rename("Deaths"),
    df_reco.sum(axis=1).rename("Recoveries")
], axis=1)
