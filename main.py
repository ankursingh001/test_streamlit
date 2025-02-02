import streamlit as st

from es_connector import  wrapper
from helper import handle_action, Action

file_path = "data.csv"

# State to hold the grid data and the current page
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'page_size' not in st.session_state:
    st.session_state.page_size = 20



# Show success message if it exists
if 'success_message' in st.session_state:
    st.success(st.session_state.success_message)
    del st.session_state.success_message
if 'error_message' in st.session_state:
    st.session_state.error_message = st.session_state.error_message
    del st.session_state.error_message
if 'warning_message' in st.session_state:
    st.warning(st.session_state.warning_message)
    del st.session_state.warning_message


input = st.text_input("Enter a search term. It will be matched across all fields.")
st.session_state.input = input

# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Choose an action:", options=[Action.UPDATE.value, Action.INSERT.value, Action.DELETE.value])
handle_action(action)





