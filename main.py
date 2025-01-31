import streamlit as st
from elasticsearch import Elasticsearch

from es_connector import SearchQueryMetaWrapper
from helper import handle_action

file_path = "data.csv"


# @st.cache_data
# def read_data():
#     return pd.read_csv(file_path)
client = Elasticsearch("http://localhost:9200")
wrapper = SearchQueryMetaWrapper(client)
df = wrapper.read_data()


# Sidebar for actions
st.sidebar.header("Actions")
action = st.sidebar.selectbox("Choose an action:", options=["upsert", "delete"])
handle_action(action, wrapper, df)





