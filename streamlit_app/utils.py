from typing import Dict

import requests
import pandas as pd
import streamlit as st
import geopandas as gpd


@st.experimental_memo()
def read_data():
    url = (
        "https://usi-icebergs.s3.eu-central-1.amazonaws.com/icebergs_locations_usi.csv"
    )
    df = pd.read_csv(url)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"], crs="EPSG:4326"),
    )
    gdf["date"] = pd.to_datetime(gdf["date"])
    gdf["extent"] = (gdf["width (nm)"] * gdf["length (nm)"]) / 2
    return gdf


def filter_data(df, iceberg_names, start_date=None, end_date=None):
    df_iceberg = df[df["iceberg"].isin(iceberg_names)]  # partial matching
    if start_date is not None and end_date is not None:
        date_mask = (df_iceberg["date"].dt.date > start_date) & (
            df_iceberg["date"].dt.date <= end_date
        )
        df_iceberg = df_iceberg.loc[date_mask]
    df_iceberg = df_iceberg.reset_index(drop=True)

    return df_iceberg


def load_lottieurl(url: str) -> Dict:
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
