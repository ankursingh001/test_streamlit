import json
import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, JsCode, AgGrid, DataReturnMode, GridUpdateMode

file_path = "data.csv"


@st.cache_data
def read_data():
    return pd.read_csv(file_path)

df = read_data()

# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Choose an action:", options=["Upsert", "Delete"])


# st.dataframe(df)
gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=True, groupable=True, resizable=True, sortable=True, filter=True)
sel_mode = st.radio('Selection type', options=["single", "multiple"])
gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
grid_options = gd.build()
grid_table = AgGrid(df, gridOptions=grid_options, update_mode=GridUpdateMode.SELECTION_CHANGED, allow_unsafe_jscode=True, height=500, theme='fresh')


sel_row = grid_table["selected_rows"]

st.write("### Selected rows")
st.write(sel_row)


