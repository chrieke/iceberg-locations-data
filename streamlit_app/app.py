import streamlit as st

import utils
import components


st.set_page_config(
    page_title="Iceberg Locations",
    layout="centered",
    page_icon="🧊",
    initial_sidebar_state="collapsed",
)

st.title(f"Iceberg Locations")
st.caption(
    "**US National Ice Center (USNIC) archive (2014-today). "
    "[More information](https://github.com/chrieke/iceberg-locations-data).**"
)
st.image("header_img.jpeg")
st.write("")

df = utils.read_data()

iceberg_names = components.data_selection(df)
start_date, end_date = components.optional_data_filters()
df_icebergs = utils.filter_data(df, iceberg_names, start_date, end_date)

st.markdown("---")

expander_text = (
    f"Results: **{len(iceberg_names)}** Icebergs - **{len(df_icebergs)}** Data points - Dates: *"
    f"*{df_icebergs['date'].min().strftime('%Y/%m/%d')}** - **{df_icebergs['date'].max().strftime('%Y/%m/%d')}**"
)

with st.expander(expander_text):
    components.data_exploration(df_icebergs)

components.vizualization(df_icebergs)

components.download(df_icebergs)
