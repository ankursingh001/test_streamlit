from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd
from pandas import json_normalize
import streamlit as st

from elasticsearch import helpers, NotFoundError, Elasticsearch

# Map Elasticsearch types to pandas types
es_to_pd_dtype = {
    "text": str,
    "keyword": str,
    "integer": int,
    "long": int,
    "float": float,
    "double": float,
    "boolean": bool,
    "date": 'datetime64[ns]',  # pandas datetime type
}



class EsWrapper(ABC):
    def __init__(self, index_name, client):
        self.index_name = index_name
        self.client = client
        self.schema = None

    @abstractmethod
    def read_data(self, query):
        pass

    @abstractmethod
    def write_data(self, df):
        pass
    @abstractmethod
    def get_df(self, query):
        pass


class SearchQueryMetaWrapper(EsWrapper):
    index_alias = "search_query_meta"

    def __init__(self, client):
        super().__init__(SearchQueryMetaWrapper.index_alias, client)
        self.schema = self.get_schema()

    def get_schema(self):
        mappings = self.client.indices.get_mapping(index=SearchQueryMetaWrapper.index_alias)

        # Extract mappings for the first index (you can modify to handle multiple indices)
        index_mapping = mappings[SearchQueryMetaWrapper.index_alias]['mappings']
        properties = index_mapping.get('properties', {})
        # Prepare the schema object
        schema = {}
        schema["_id"] = 'str'
        self.client.indices.get_mapping(index=SearchQueryMetaWrapper.index_alias)
        for field, details in properties.items():
            field_type = details.get('type')
            if field_type in es_to_pd_dtype:
                schema[field] = es_to_pd_dtype[field_type]
        return schema

    def get_df(self):
        hits = self.read_data(st.session_state.input, st.session_state.page, st.session_state.page_size)
        if hits:
            # Extract source data to a pandas DataFrame
            data = [{**hit['_source'], '_id': hit['_id']} for hit in hits]
            df = json_normalize(data)
            # Step 5: Apply schema to DataFrame
            for column, dtype in self.schema.items():
                if column in df.columns:
                    if dtype == bool:
                        df[column] = df[column].map({"True": True, "False": False})
                    else:
                        df[column] = df[column].astype(dtype)
            column_order = ['_id'] + [col for col in df.columns if col != '_id']
            df = df[column_order]  # Reorder the DataFrame
            df.fillna('', inplace=True)
            st.session_state.current_df = df
            return df
        return pd.DataFrame()

    def read_data(_self, query, page, page_size):
        # Example query to retrieve documents
        page = st.session_state.page
        page_size = st.session_state.page_size

        # Step 1: Check total hits
        if not query:
            total_page_query = {
                "query": {
                    "match_all": {}
                }
            }
        else:
            total_page_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"]
                    }
                }
            }
        page_response = _self.client.search(index=_self.index_alias, body=total_page_query, size=0)  # size=0 to avoid returning actual documents

        total_hits = page_response['hits']['total']['value']  # For ES 7.x and above

        max_pages = (total_hits + page_size - 1) // page_size  # Calculate maximum number of pages
        page = min(max_pages, page)

        if not query:
            response = _self.client.search(
                index=_self.index_alias,  # Replace with the name of your index
                body={
                    "query": {
                        "match_all": {}
                    },
                    "size": page_size,
                    "from": (page - 1) * page_size,
                    "sort": [
                        {
                            "_score": {  # Sort by relevance score
                                "order": "desc"
                            }
                        }
                    ]
                }
            )
        else:
            response = _self.client.search(index=_self.index_alias, body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"]  # Search across all fields
                    }
                },
                "size": page_size,
                "from": (page - 1) * page_size,
                "sort": [
                    {
                        "_score": {  # Sort by relevance score
                            "order": "desc"
                        }
                    }
                ],
            })
        hits = response['hits']['hits']
        if not hits:
            st.error("ES returned no results.")
            return None
        return hits

    def write_data(self, updated_rows):
        # Convert the DataFrame to a format suitable for Elasticsearch
        actions = [
            {
                "_index": SearchQueryMetaWrapper.index_alias,  # Replace with your desired index name
                "_id": record["_id"],  # Optional: use index or a field value as the document ID
                "_source": {key: value for key, value in record.items() if key != "_id"}
            }
            for record in updated_rows.to_dict(orient='records')
        ]
        response = None
        try:
            # Use bulk helper to index documents
            response = helpers.bulk(self.client, actions)
            st.session_state.success_message = "Data has been written to Elasticsearch!"
        except Exception as e:
            # Attempt to delete the index if the bulk operation fails
            st.session_state.error_message = f"An error occurred while writing data to Elasticsearch: {e}"
            # Print response if available
            if 'items' in response:
                for item in response['items']:
                    # Check for failures
                    if 'index' in item and 'error' in item['index']:
                        print(f"Failed to index document ID: {item['index']['_id']}, Error: {item['index']['error']}")
            return

    def delete_data(self, sel_row):
        st.write("### Delete data")
        if sel_row is not None:
            st.write(sel_row)
            # Add a Delete button
            if not sel_row.empty:
                for row in sel_row.iterrows():
                    doc_id = row[1]['_id']
                    try:
                        self.client.delete(index=self.index_alias, id=doc_id)
                        st.session_state.success_message = f"Deleted document with ID: {doc_id} from Elasticsearch."
                    except NotFoundError:
                        st.session_state.warning_message = f"Document with ID: {doc_id} not found in Elasticsearch."
                    except Exception as e:
                        st.session_state.error_message = f"Error deleting document ID {doc_id}: {e}"
            else:
                 st.session_state.error_message = "No rows selected for deletion."

client = Elasticsearch("http://localhost:9200")
wrapper = SearchQueryMetaWrapper(client)