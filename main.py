import json
from enum import Enum

import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, JsCode, AgGrid, DataReturnMode, GridUpdateMode

from helper import Action, get_grid_by_operation, handle_action

file_path = "data.csv"


@st.cache_data
def read_data():
    return pd.read_csv(file_path)


df = read_data()


# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Choose an action:", options=["upsert", "delete"])
handle_action(action, df)





