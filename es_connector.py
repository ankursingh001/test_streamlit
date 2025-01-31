from abc import ABC, abstractmethod
from datetime import datetime

from pandas import json_normalize
import streamlit as st

from elasticsearch import helpers

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
    def read_data(self):
        pass

    @abstractmethod
    def write_data(self):
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
        self.client.indices.get_mapping(index=SearchQueryMetaWrapper.index_alias)
        for field, details in properties.items():
            field_type = details.get('type')
            if field_type in es_to_pd_dtype:
                schema[field] = es_to_pd_dtype[field_type]
        return schema

    @st.cache_data
    def read_data(_self):
        # Example query to retrieve documents
        response = _self.client.search(
            index=_self.index_alias,  # Replace with the name of your index
            body={
                "query": {
                    "match_all": {}
                },
                "size": 10000  # Set to a number that encompasses all expected results (maximum is 10000)
            }
        )
        hits = response['hits']['hits']
        # Extract source data to a pandas DataFrame
        data = [hit['_source'] for hit in hits]
        df = json_normalize(data)
        # Step 5: Apply schema to DataFrame
        for column, dtype in _self.schema.items():
            if column in df.columns:
                if dtype == bool:
                    df[column] = df[column].map({"True": True, "False": False})
                else:
                    df[column] = df[column].astype(dtype)

        # Step 6: Display the resulting DataFrame and its dtypes
        print(df)
        df.fillna('', inplace=True)
        return df

    def write_data(self, df):
        # Convert the DataFrame to a format suitable for Elasticsearch
        records = df.to_dict(orient='records')  # Convert to list of dictionaries
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        index_name = f"search_query_meta-{timestamp}"
        # Retrieve the mapping from the existing index
        mapping = self.client.indices.get_mapping(index=SearchQueryMetaWrapper.index_alias)
        # Use the mapping of the first index in case of multiple index aliases
        index_mapping = mapping[SearchQueryMetaWrapper.index_alias]['mappings']

        # Create the new index with the retrieved mapping
        self.client.indices.create(index=index_name, body={"mappings": index_mapping})
        # Prepare actions for the bulk API
        actions = [
            {
                "_index": index_name,  # Replace with your desired index name
                "_id": index,  # Optional: use index or a field value as the document ID
                "_source": record
            }
            for index, record in zip(df.index, records)  # Create action for each record
        ]
        response = None
        try:
            # Use bulk helper to index documents
            response = helpers.bulk(self.client, actions)
            st.success("Data has been written to Elasticsearch!")
        except Exception as e:
            # Attempt to delete the index if the bulk operation fails
            st.error(f"An error occurred while writing data to Elasticsearch: {e}")
            # Print response if available
            if 'items' in response:
                for item in response['items']:
                    # Check for failures
                    if 'index' in item and 'error' in item['index']:
                        print(f"Failed to index document ID: {item['index']['_id']}, Error: {item['index']['error']}")
            if self.client.indices.exists(index=index_name):
                self.client.indices.delete(index=index_name)
                st.info(f"Deleted index: {index_name}")
            return
        try:
            # Point the alias to the new index
            self.client.indices.update_aliases(
                actions=[
                    {"remove": {"index": SearchQueryMetaWrapper.index_alias, "alias": "search_query_meta"}},
                    {"add": {"index": index_name, "alias": "search_query_meta"}}
                ])

            st.success(f"Alias 'search_query_meta' has been pointed to the new index {index_name}.")
        except Exception as e:
            st.error(f"An error occurred while updating the alias: {e}")
            st.error(f"Please ensure that the alias {SearchQueryMetaWrapper.index_alias} is correctly set up.")



