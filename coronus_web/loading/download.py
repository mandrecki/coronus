
import numpy as np
import pandas as pd
import logging
from pkg_resources import resource_listdir, resource_stream

import coronus_web


GEO_LEVELS = [
    # "city",
    # "county",
    "state",
    "country",
    "continent",
    "global",
]

CASE_TYPES = [
    "active",
    "deaths",
    "confirmed",
    "recovered",
    "tested",
    # "active_derived",
]


def get_geo_codes():
    codes = pd.read_csv(resource_stream(coronus_web.__name__, "data/JohnSnowLabs/country-and-continent-codes-list-csv_csv.csv"))
    codes = codes.set_index("Three_Letter_Country_Code")

    simple_country_names = pd.read_csv(resource_stream(coronus_web.__name__, "data/tadast/countries_codes_and_coordinates.csv"))
    simple_country_names["Alpha-3 code"] = simple_country_names["Alpha-3 code"].map(lambda x: x[2:-1])
    simple_country_names = simple_country_names.set_index("Alpha-3 code")

    codes = codes.merge(simple_country_names[["Country"]], left_index=True, right_index=True,
                                        how="inner")
    codes = codes.rename(columns={
        "Continent_Name": "continent",
        "Country": "country",
    })
    codes = codes.drop(columns=[col for col in codes.columns if col not in GEO_LEVELS])

    return codes


def get_new_frames() -> (pd.DataFrame, pd.DataFrame):
    """
    Generates DataFrames for different cases and geo_levels, as well as geography Dataframe with region naming conventions
    population and location.
    """

    cases = pd.read_csv("https://coronadatascraper.com/timeseries.csv", parse_dates=["date"])

    # FIXME very naive approach without testing!!!
    # cases = cases.drop_duplicates(["country", "date"])

    cases = cases.rename(columns={
        "country": "country_code",
        "cases": "confirmed",
    })
    cases["global"] = "global"

    codes = get_geo_codes()
    cases = cases.merge(
        codes,
        left_on="country_code",
        right_index=True,
        how="left"
    )

    geography = cases[GEO_LEVELS + ["country_code", "lat", "long", "population"]].drop_duplicates(GEO_LEVELS)
    cases["active_derived"] = (cases["confirmed"] - cases["recovered"] - cases["deaths"])

    cases_by_geolevel = {
        geo_level:
            {
                case_type: cases[["date", geo_level, case_type]]
                    .groupby(["date", geo_level])[case_type].sum().unstack().replace(0, np.nan).dropna(axis=1, how='all').fillna(method="ffill")  # FIXME added filling values by copying from past!!
                for case_type in CASE_TYPES}
        for geo_level in GEO_LEVELS
    }

    return cases_by_geolevel, geography



################################## OLD ########################################
#
# urls = dict(
#     confirmed="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
#     recovered="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
#     deaths="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
# )
#
# def get_continents():
#     stream = resource_stream(coronus_web.__name__, "data/country_to_continent.csv")
#     df = pd.read_csv(stream, encoding = "iso-8859-1")
#     return df
#
#
# def append_continents(cases, continents):
#     cases_with_continents = cases.merge(
#         continents,
#         on="country",
#         how="left")
#     # Avoid failure if new countries were added that we are not handling yet
#     cases_with_continents = cases_with_continents.fillna("Unassigned")
#     if "Unassigned" in cases_with_continents.continent:
#         logging.warning("Country without a continent! Add row to data/country_to_continent.csv \n"
#                         "{}".format(cases_with_continents[cases_with_continents.Continent == "Unassigned"].country))
#
#     return cases_with_continents
#
#
# def get_raw_df(url):
#     #     s = requests.get(url).content
#     #     df = pd.read_csv(io.StringIO(s.decode('utf-8')))
#     df = pd.read_csv(url)
#     df = df.rename(columns={
#         "Province/State": "state",
#         "Country/Region": "country",
#         "Lat": "lat",
#         "Long": "long",
#     })
#     df["global"] = "global"
#     df.loc[df["state"].isna(), "state"] = df.loc[df["state"].isna(), "country"]
#     return df
#
#
# def to_spacetime(df, geolevel: str):
#     drop_cols = GEO_LEVELS + ["lat", "long"]
#     drop_cols.remove(geolevel)
#     df = df.drop(columns=drop_cols)
#     df = df.groupby(geolevel).sum()
#     df = df.T
#     df.index.name = "date"
#     df.index = pd.to_datetime(df.index)
#     return df
#
#
# def calculate_active(spacetime_dict):
#     active = spacetime_dict["confirmed"] - spacetime_dict["recovered"] - spacetime_dict["deaths"]
#     return active.replace(0, np.nan)
#
#
# def get_frames():
#     continents = get_continents()
#
#     cases_raw = {
#         case_type:
#             append_continents(get_raw_df(url), continents)
#         for case_type, url in urls.items()
#     }
#
#     geography = cases_raw["confirmed"][GEO_LEVELS + ["lat", "long"]]
#     cases_by_geolevel = dict()
#     for geolevel in GEO_LEVELS:
#         spacetime = {count_type: to_spacetime(cases_raw[count_type], geolevel=geolevel) for count_type in cases_raw.keys()}
#         spacetime["active"] = calculate_active(spacetime)
#         cases_by_geolevel[geolevel] = spacetime
#
#     return cases_by_geolevel, geography