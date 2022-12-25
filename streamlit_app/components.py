import datetime
from dateutil.parser import parse

import streamlit as st
import plotly.express as px


def data_selection(df):
    icebergs = sorted(list(df["iceberg"].unique()))

    col1_filter, col2_filter = st.columns((6, 1.5))
    col2_filter.write("")
    col2_filter.write("")
    select_all = col2_filter.checkbox("Select All")
    if not select_all:
        iceberg_names = col1_filter.multiselect(
            "Select Icebergs", icebergs, default=["A56", "B15T", "A23A", "B30"]
        )
    else:
        iceberg_names = col1_filter.multiselect(
            "Select Icebergs", icebergs, default=icebergs
        )

    return iceberg_names


def optional_data_filters():
    start_date, end_date = None, None
    with st.expander("More filters: time, area etc. (Click to Expand)"):
        date1, date2, _, date3, _ = st.columns(5)
        date1_empty = date1.empty()
        date2_empty = date2.empty()
        start_date = date1_empty.date_input(
            "Start date",
            value=parse("2014-01-07"),
            min_value=parse("2014-01-07"),
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

        st.write("Aoi filter etc.")

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
    st.dataframe(avg_df, height=190)


def vizualization(df):
    df["date"] = df["date"].astype(str)
    df = df.sort_values(["date"], axis=0)

    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        size="extent",
        color="iceberg",
        animation_frame="date",
        hover_name="iceberg",
        size_max=30,
        color_discrete_sequence=px.colors.qualitative.Alphabet,
    ).update_traces(
        marker=dict(line=dict(width=0)),
        selector=dict(mode="markers"),
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0}, showlegend=False, height=700
    )

    fig.update_layout(
        geo=dict(
            resolution=50,
            showland=True,
            showcountries=True,
            showocean=True,
            countrywidth=0.5,
            landcolor="rgb(255, 255, 255)",
            lakecolor="rgb(0, 255, 255)",
            oceancolor="rgb(161, 207, 227)",
            projection=dict(type="orthographic", rotation=dict(lon=0, lat=-90, roll=0)),
            lonaxis=dict(showgrid=True, gridcolor="rgb(102, 102, 102)", gridwidth=0.5),
            lataxis=dict(showgrid=True, gridcolor="rgb(102, 102, 102)", gridwidth=0.5),
        )
    )

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 1
    fig.layout.sliders[0].pad.t = 10
    fig.layout.updatemenus[0].pad.t = 10

    st.plotly_chart(fig)


def download(df):
    dl1, dl2, dl3, _ = st.columns([0.7, 1, 1, 2])
    dl1.markdown("**Download**")
    # st.download_button("⬇️ GeoJSON", df.to_json(), "iceberg.geojson")
    st.download_button("⬇️ CSV", df.to_csv(), "iceberg.csv")
