import streamlit as st
from streamlit_lottie import st_lottie

import utils
import components


st.set_page_config(
    page_title="Iceberg locations",
    layout="centered",
    page_icon="🧊",
    initial_sidebar_state="collapsed",
)

col1_header, col2_header = st.columns([1, 6])
lottie_url = "https://assets8.lottiefiles.com/packages/lf20_nfr5xpxm.json"
lottie_json = utils.load_lottieurl(lottie_url)
with col1_header:
    st_lottie(lottie_json, height=115, speed=1)

col2_header.write("")
col2_header.title(f"Iceberg")
st.markdown(
    "**Explore the US National Ice Center data (2014-today), see "
    "[more information](https://github.com/chrieke/iceberg-locations-data)**"
)
st.write("")

df = utils.read_data()

iceberg_names = components.data_selection(df)
start_date, end_date = components.optional_data_filters()
df_icebergs = utils.filter_data(df, iceberg_names, start_date, end_date)

st.markdown("---")
st.markdown(
    f"**{len(iceberg_names)}** Icebergs - **{len(df_icebergs)}** Data points - Dates: **{df_icebergs['date'].min().strftime('%Y/%m/%d')}** - **{df_icebergs['date'].max().strftime('%Y/%m/%d')}**"
)
st.write("")
components.data_exploration(df_icebergs)

components.download(df_icebergs)

# components.vizualization(df_icebergs)
