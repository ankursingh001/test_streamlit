from pandas import json_normalize
import streamlit as st

from elasticsearch import Elasticsearch

client = Elasticsearch(
      "http://localhost:9200"
)
index= 'search_query_meta'
# Assuming 'client' is your Elasticsearch client and 'index' is your index name
mappings = client.indices.get_mapping(index=index)


# Extract mappings for the first index (you can modify to handle multiple indices)
index_mapping = mappings[index]['mappings']
properties = index_mapping.get('properties', {})

# Prepare the schema object
schema = {}

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

for field, details in properties.items():
    field_type = details.get('type')
    if field_type in es_to_pd_dtype:
        schema[field] = es_to_pd_dtype[field_type]

print(schema)  # This will show you the schema mapping


@st.cache_data
def get_data_frame_from_es(index):
    # Example query to retrieve documents
    response = client.search(
        index=index,  # Replace with the name of your index
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
    for column, dtype in schema.items():
        if column in df.columns:
            if dtype == bool:
                df[column] = df[column].map({"True": True, "False": False})
            else:
                df[column] = df[column].astype(dtype)

    # Step 6: Display the resulting DataFrame and its dtypes
    print(df)
    df.fillna('', inplace=True)
    return df