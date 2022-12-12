from shapely.geometry import LineString
import datetime
from dateutil.parser import parse

import streamlit as st
import holoviews as hv
import hvplot.pandas

import utils


def data_selection(df):
    icebergs = sorted(list(df["iceberg"].unique()))

    col1_filter, col2_filter = st.columns((6, 1.5))
    col2_filter.write("")
    col2_filter.write("")
    select_all = col2_filter.checkbox("Select All")
    if not select_all:
        iceberg_names = col1_filter.multiselect(
            "Select Icebergs", icebergs, default=["D32"]  # "A68D", "A68C"
        )
    else:
        iceberg_names = col1_filter.multiselect(
            "Select Icebergs", icebergs, default=icebergs
        )

    return iceberg_names


def optional_data_filters():
    start_date, end_date = None, None
    with st.expander("More Filters (Click to Expand)"):
        date1, date2, _, date3, _ = st.columns(5)
        date1_empty = date1.empty()
        date2_empty = date2.empty()
        start_date = date1_empty.date_input(
            "Start date",
            value=parse("2017-11-07"),
            min_value=parse("2017-11-07"),
            max_value=datetime.date.today(),
            key="123",
        )
        end_date = date2_empty.date_input(
            "End date",
            value=datetime.date.today(),
            min_value=parse("2017-11-07"),
            max_value=datetime.date.today(),
            key="456",
        )
        date3.write("")
        date3.write("")
        reset_dates = date3.button("Reset Dates")
        if reset_dates:
            # RESET DATE
            start_date = date1_empty.date_input(
                "Start date",
                value=parse("2017-11-07"),
                min_value=parse("2017-11-07"),
                max_value=datetime.date.today(),
                key="1231",
            )
            end_date = date2_empty.date_input(
                "End date",
                value=datetime.date.today(),
                min_value=parse("2017-11-07"),
                max_value=datetime.date.today(),
                key="4564",
            )

        return start_date, end_date


def data_exploration(df_icebergs):
    avg_df = (
        df_icebergs.drop(["geometry"], axis=1)
        .groupby(["iceberg"])
        .mean(numeric_only=True)
    )
    avg_df["nr #"] = df_icebergs.groupby(["iceberg"]).date.count()
    avg_df["first #"] = df_icebergs.groupby(["iceberg"]).date.min()
    avg_df["last #"] = df_icebergs.groupby(["iceberg"]).date.max()
    st.dataframe(avg_df, height=150)


def vizualization(df):
    # Remove instances with only one occurence, can not be visualized as path
    df = df.groupby(["iceberg"]).filter(lambda x: len(x["geometry"].tolist()) >= 2)
    lines = list(
        df.groupby(["iceberg"]).apply(lambda x: LineString(x["geometry"].tolist()))
    )
    df_lines = df.drop(["geometry"], axis=1).groupby(["iceberg"]).first().reset_index()
    df_lines["geometry"] = lines
    df_lines = df_lines.set_geometry("geometry")

    st.write("aa")
    # DATA VIZ
    points_plot = df.hvplot.points(
        coastline=True,
        color="iceberg",
        alpha=0.8,
        padding=0.3,
        hover_cols="all",
    )
    st.write("bb")
    lines_plot = df_lines.hvplot.paths(
        coastline=True,
        tiles="ESRI",
        padding=0.3,
        color="red",
        legend="top",
    )

    hv_plot = (lines_plot * points_plot).opts(
        toolbar="right",
        active_tools=["wheel_zoom"],
        xlabel="",
        ylabel="",
        width=700,
        height=500,
    )

    # from bokeh.models.glyphs import ImageURL
    # url = "https://bokeh.pydata.org/en/latest/_static/images/logo.png"
    # N = 5
    # image1 = ImageURL(url="url", x="x1", y="y1", w="w1", h="h1", anchor="center")
    # hv_plot.add_glyph(source, image1)

    # 2 hvplots side by side with "+", on top with "*"
    hv_render = hv.render(hv_plot, backend="bokeh")
    st.bokeh_chart(hv_render)


def download(df):
    dl1, dl2, dl3, _ = st.columns([0.7, 1, 1, 2])
    dl1.markdown("**Download**")
    # st.download_button("⬇️ GeoJSON", df.to_json(), "iceberg.geojson")
    st.download_button("⬇️ CSV", df.to_csv(), "iceberg.csv")
