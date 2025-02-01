import streamlit as st

from es_connector import  wrapper
from helper import handle_action

file_path = "data.csv"

# State to hold the grid data and the current page
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'page_size' not in st.session_state:
    st.session_state.page_size = 50
if 'current_df' not in st.session_state:
    st.session_state.current_df = None

input = st.text_input("Enter a search term. It will be matched across all fields.")
# if not st.session_state.updated:
st.session_state.current_df = wrapper.get_df(input)

# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Choose an action:", options=["upsert", "delete"])
handle_action(action, wrapper)





